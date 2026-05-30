import os
import socket
import sys
import importlib
import threading
import logging
import signal
from pathlib import Path

from sbdots.library.logger import setup_daemon_logging
from sbdots.actions._base import BaseAction
from sbdots.constants import VALID_ACTIONS


setup_daemon_logging("SBDotsActionsDaemon")
logger = logging.getLogger("SBDotsActionsDaemon")

try:
    import setproctitle

    setproctitle.setproctitle("sbdots-actions-d")

except Exception as e:
    logger.warning(
        "An unexpected error while setting process title",
        extra={"daemon": "actions"},
        exc_info=e,
    )
    pass

RUNTIME_DIR = Path(os.getenv("XDG_RUNTIME_DIR", "/tmp"))
SOCKET_PATH = RUNTIME_DIR / "sbdots-actions.sock"


# For tracking connections and running actions
RUNNING_ACTIONS = list()
ACTIVE_CONNECTIONS = 0
STATE_LOCK = threading.Lock()
ACTION_TIMEOUT = 30

# For handling graceful shutdown
SHUTDOWN_EVENT = threading.Event()


def log_daemon_status(event: str):
    """Logs the current status of the daemon."""
    with STATE_LOCK:
        status = (
            f"Event: {event} | "
            f"Clients: {ACTIVE_CONNECTIONS} | "
            f"Running: {RUNNING_ACTIONS or '[]'}"
        )
        logger.info(status)


def signal_handler(sig, frame):
    """Sets the shutdown event when a signal is received."""
    logger.info(f"Signal {sig} received. Initiating graceful shutdown...")
    SHUTDOWN_EVENT.set()


def error(conn, message: str):
    """Safely send a message to the client."""
    logger.error(message)

    if SHUTDOWN_EVENT.is_set():
        logger.debug("Shutdown in progress. Suppressing send.")
        return

    payload = ("Error: " + message + "\n").encode()

    try:
        conn.sendall(payload)
    except BrokenPipeError:
        logger.debug("Client disconnected before response could be sent.")
    except Exception as e:
        logger.warning(f"Failed to send message to client: {e}")


def load_action(name: str, conn) -> type[BaseAction] | None:
    """Import the action 'name' from sbdots.actions and return the main action class"""

    if name not in VALID_ACTIONS:
        error(
            conn,
            f"Invalid action '{name}', valid actions: {VALID_ACTIONS}.",
        )
        return None

    try:
        module = importlib.import_module(f"sbdots.actions.{name}")

    except Exception as e:
        error(conn, f"Failed to import action '{name}': {e}")
        return None

    # i.e: get_weather_data -> GetWeatherData
    class_name = "".join(part.capitalize() for part in name.split("_"))

    if not hasattr(module, class_name):
        error(
            conn,
            f"No class '{class_name}' found in actions.{name}",
        )
        return None

    _class = getattr(module, class_name)

    if not issubclass(_class, BaseAction):
        error(conn, f"'{_class}' is not a valid action class.")
        return None

    return _class


def run_action(name: str, cls_instance, conn) -> None:
    try:
        cls_instance.main()
        logger.debug(f"Action '{name}' completed successfully.")

    except Exception as e:
        error(conn, f"Error during '{name}'.main() execution: {e}")


def rm_prev_socket() -> None:
    """
    Remove existing socket path
    """
    try:
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
    except OSError as e:
        if os.path.exists(SOCKET_PATH):
            logger.error(f"Failed to remove existing socket: {e}")
            sys.exit(1)


def handle_shutdown(active_threads: set) -> None:
    """Shutdown the daemon gracfully"""

    logger.info("Shutdown initiated. Waiting for active actions to complete...")

    with STATE_LOCK:
        current_threads = list(active_threads)

    for thread in current_threads:
        if thread.is_alive():
            thread.join(timeout=2)
            if thread.is_alive():
                logger.warning("Thread failed to terminate within timeout")

    logger.info("All actions finished. Daemon shut down.")


def handle_action(conn):
    """Handles a single client connection and action execution."""
    global RUNNING_ACTIONS
    action_name = "unknown"

    try:
        data = conn.recv(1024).decode().strip()
        if not data:
            error(conn, "Empty request")
            return

        parts = data.split(" ")
        action_name = parts[0]
        action_args = parts[1:]

        ActionClass = load_action(action_name, conn)
        if ActionClass is None:
            return

        # ACTIONS STARTING PROCCESS STARTS FROM HERE
        log_daemon_status(f"Action '{action_name}' started")

        try:
            instance = ActionClass(conn, *action_args)
        except Exception as e:
            error(conn, f"Failed to initialize '{action_name}': {e}")
            return

        # Register
        with STATE_LOCK:
            RUNNING_ACTIONS.append(action_name)

        run_action(action_name, instance, conn)

    except (ConnectionResetError, BrokenPipeError):
        logger.exception("Client disconnected unexpectedly: ")
    except Exception as e:
        logger.exception("Unexpected error in handle_action: ")
        try:
            error(conn, f"Unexpected server error: {e}")
        except Exception:
            pass

    # Unregister
    finally:
        if action_name in RUNNING_ACTIONS:
            RUNNING_ACTIONS.remove(action_name)

        log_daemon_status(f"Action '{action_name}' finished")
        conn.close()


def start_daemon():
    """Starts the actions daemon and listens for connections."""
    global ACTIVE_CONNECTIONS

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    rm_prev_socket()

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(str(SOCKET_PATH))
        os.chmod(SOCKET_PATH, 0o600)
        s.listen()
        s.settimeout(1.0)  # Non-blocking accept to check shutdown flag
        logger.info(f"Daemon started. Listening on {SOCKET_PATH}...")

        active_threads = set()

        while not SHUTDOWN_EVENT.is_set():
            try:
                conn, _ = s.accept()
            except socket.timeout:
                with STATE_LOCK:
                    finished_threads = [t for t in active_threads if not t.is_alive()]
                    for thread in finished_threads:
                        active_threads.remove(thread)
                continue

            with STATE_LOCK:
                ACTIVE_CONNECTIONS += 1

            log_daemon_status("Client connected")

            def client_thread_wrapper(conn_arg):
                global ACTIVE_CONNECTIONS
                try:
                    handle_action(conn_arg)
                finally:
                    with STATE_LOCK:
                        ACTIVE_CONNECTIONS -= 1
                    log_daemon_status("Client disconnected")

            thread = threading.Thread(
                target=client_thread_wrapper, args=(conn,), daemon=True
            )
            thread.start()
            with STATE_LOCK:
                active_threads.add(thread)

        # Shutdown event is set
        handle_shutdown(active_threads)

    # Final cleanup
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)


if __name__ == "__main__":
    try:
        start_daemon()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
