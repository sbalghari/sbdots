# actions daemon/local-server

import os
import socket
import sys
import importlib
import threading
import logging
import io
import signal
import concurrent.futures
from contextlib import redirect_stdout
from typing import Dict, List

import actions  # noqa: F401


SOCKET_PATH = "/tmp/sbdots_actions.sock"
LONG_RUNNING_ACTIONS: List[Dict] = []
ACTION_TIMEOUT = 30  # seconds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("SBDotsActionsDaemon")

# --- Global State ---
# For tracking connections and running actions
state_lock = threading.Lock()
active_connections = 0
running_actions = []

# For handling graceful shutdown
shutdown_event = threading.Event()


def log_daemon_status(event: str):
    """Logs the current status of the daemon."""
    with state_lock:
        status = (
            f"Event: {event} | "
            f"Clients: {active_connections} | "
            f"Running: {running_actions or '[]'}"
        )
        logger.info(status)


def signal_handler(sig, frame):
    """Sets the shutdown event when a signal is received."""
    logger.info(f"Signal {sig} received. Initiating graceful shutdown...")
    shutdown_event.set()


def send(conn, message: str):
    """Safely send a message to the client."""
    if shutdown_event.is_set():
        logger.debug("Shutdown in progress. Suppressing send.")
        return
    try:
        conn.send(message.encode())
    except BrokenPipeError:
        logger.debug("Client disconnected before response could be sent.")
    except Exception as e:
        logger.warning(f"Failed to send message to client: {e}")


def handle_action(conn):
    """Handles a single client connection and action execution."""
    global running_actions
    action2exec = "unknown"
    is_long_running = False

    try:
        data = conn.recv(1024).decode().strip()
        if not data:
            send(conn, "ERROR: Empty request")
            return

        parts = data.split(" ")
        action2exec = parts[0]
        args4action = parts[1:]

        try:
            module = importlib.import_module(f"actions.{action2exec}")
        except Exception as e:
            msg = f"Failed to import action '{action2exec}': {e}"
            logger.error(msg)
            send(conn, f"ERROR: {msg}")
            return

        class_name = "".join(part.capitalize() for part in action2exec.split("_"))
        if not hasattr(module, class_name):
            msg = f"No class '{class_name}' found in actions.{action2exec}"
            logger.error(msg)
            send(conn, f"ERROR: {msg}")
            return

        ActionClass = getattr(module, class_name)
        is_long_running = getattr(ActionClass, "is_long_running", False)
        action_name = ActionClass.__name__

        # Remove if already running
        if is_long_running:
            with state_lock:
                to_remove = None
                for entry in LONG_RUNNING_ACTIONS:
                    if entry["name"] == action_name:
                        logger.warning(
                            f"Long running action [{action2exec}] is already running. Stopping it first..."
                        )
                        try:
                            if hasattr(entry["instance"], "stop"):
                                entry["instance"].stop()
                            entry["conn"].close()
                        except Exception as e:
                            logger.warning(
                                f"Failed to stop previous '{entry['name']}': {e}"
                            )
                        to_remove = entry
                        break

                if to_remove:
                    LONG_RUNNING_ACTIONS.remove(to_remove)

        with state_lock:
            if action2exec not in running_actions:
                running_actions.append(action2exec)
        log_daemon_status(f"Action '{action2exec}' started")

        # Pass connection to long-running actions, otherwise instantiate normally
        try:
            if is_long_running:
                instance = ActionClass(conn, *args4action)
                with state_lock:
                    LONG_RUNNING_ACTIONS.append(
                        {
                            "name": action_name,
                            "instance": instance,
                            "thread": threading.current_thread(),
                            "conn": conn,
                        }
                    )
            else:
                instance = ActionClass(conn, *args4action)
        except Exception as e:
            msg = f"Failed to initialize '{class_name}': {e}"
            logger.error(msg)
            send(conn, f"ERROR: {msg}")
            return

        if not hasattr(instance, "main"):
            send(conn, "ERROR: No main() method found")
            return

        if is_long_running:

            def long_running_wrapper():
                try:
                    instance.main()
                except Exception as e:
                    logger.error(f"Long-running action '{action_name}' crashed: {e}")
                    try:
                        send(conn, f"ERROR: Action crashed: {e}")
                    except Exception:
                        pass  # Connection might already be closed
                    # Clean up the failed action
                    with state_lock:
                        for entry in LONG_RUNNING_ACTIONS[:]:
                            if entry["name"] == action_name:
                                LONG_RUNNING_ACTIONS.remove(entry)
                                break

            thread = threading.Thread(target=long_running_wrapper, daemon=True)
            thread.start()
        else:
            # Short-lived Action Execution with Timeout
            stdout_capture = io.StringIO()

            def action_runner():
                with redirect_stdout(stdout_capture):
                    instance.main()

            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(action_runner)
                    future.result(timeout=ACTION_TIMEOUT)

                captured_output = stdout_capture.getvalue().strip()
                send(conn, captured_output or "OK")
                logger.debug(f"Action '{action2exec}' completed successfully.")

            except concurrent.futures.TimeoutError:
                msg = f"Action '{action2exec}' timed out after {ACTION_TIMEOUT}s"
                logger.error(msg)
                send(conn, f"ERROR: {msg}")
            except Exception as e:
                msg = f"Error during '{action2exec}' execution: {e}"
                logger.error(msg, exc_info=True)
                send(conn, f"ERROR: {msg}")

    except (ConnectionResetError, BrokenPipeError):
        logger.warning("Client disconnected unexpectedly")
    except Exception as e:
        logger.exception(f"Unexpected error in handle_action: {e}")
        # Avoid sending on a potentially broken connection
    finally:
        with state_lock:
            try:
                if not is_long_running:
                    running_actions.remove(action2exec)
            except ValueError:
                pass

        if not is_long_running:
            log_daemon_status(f"Action '{action2exec}' finished")
            conn.close()


def start_daemon():
    """Starts the actions daemon and listens for connections."""
    global active_connections

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
    except OSError as e:
        if os.path.exists(SOCKET_PATH):
            logger.error(f"Failed to remove existing socket: {e}")
            sys.exit(1)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.bind(SOCKET_PATH)
        os.chmod(SOCKET_PATH, 0o600)
        s.listen()
        s.settimeout(1.0)  # Non-blocking accept to check shutdown flag
        logger.info(f"Daemon started. Listening on {SOCKET_PATH}...")

        active_threads = set()
        threads_lock = threading.Lock()

        while not shutdown_event.is_set():
            try:
                conn, _ = s.accept()
            except socket.timeout:
                with threads_lock:
                    finished_threads = [t for t in active_threads if not t.is_alive()]
                    for thread in finished_threads:
                        active_threads.remove(thread)
                continue

            with state_lock:
                active_connections += 1
            log_daemon_status("Client connected")

            def client_thread_wrapper(conn_arg):
                global active_connections
                try:
                    handle_action(conn_arg)
                finally:
                    with state_lock:
                        active_connections -= 1
                    log_daemon_status("Client disconnected")

            thread = threading.Thread(
                target=client_thread_wrapper, args=(conn,), daemon=True
            )
            thread.start()
            with threads_lock:
                active_threads.add(thread)

        logger.info("Shutdown initiated. Waiting for active actions to complete...")

        # Stop long-running actions
        with state_lock:
            for entry in LONG_RUNNING_ACTIONS[:]:
                name = entry["name"]
                inst = entry["instance"]
                conn = entry["conn"]
                logger.info(f"Forcing shutdown of long-running action '{name}'")
                try:
                    if hasattr(inst, "stop"):
                        inst.stop()
                except Exception as e:
                    logger.warning(f"Failed to stop '{name}': {e}")
            LONG_RUNNING_ACTIONS.clear()

        with threads_lock:
            current_threads = list(active_threads)

        for thread in current_threads:
            if thread.is_alive():
                thread.join(timeout=5.0)
                if thread.is_alive():
                    logger.warning("Thread failed to terminate within timeout")

        logger.info("All actions finished. Daemon shut down.")

    # Final cleanup
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)


if __name__ == "__main__":
    try:
        start_daemon()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
