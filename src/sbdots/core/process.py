import os
import psutil
import signal
import time
import shlex
import subprocess
from typing import Optional, Union, List
from typing import Iterable

from sbdots.utils.exceptions import ProcessNotKilled, ProcessError
from sbdots.utils.logger import get_caller_logger


def get_procs(name: str, logger=None) -> List[psutil.Process]:
    """Return all processes matching 'name'."""
    logger = logger or get_caller_logger()
    logger.debug(f"Getting processes matching name: {name}")
    name = name.lower()
    procs = []
    for p in psutil.process_iter(["name", "exe", "cmdline"]):
        try:
            info = p.info
            if (
                info["name"]
                and info["name"].lower() == name
                or info["exe"]
                and os.path.basename(info["exe"]).lower() == name
                or info["cmdline"]
                and info["cmdline"][0].lower() == name
            ):
                procs.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    logger.debug(f"Found {len(procs)} processes matching '{name}'")
    return procs


def get_proc(name: str, logger=None) -> Optional[psutil.Process]:
    """Return the first process matching 'name'."""
    logger = logger or get_caller_logger()
    logger.debug(f"Getting first process matching name: {name}")
    proc = get_procs(name)
    result = proc[0] if proc else None
    logger.debug(f"Found process: {result.pid if result else 'None'}")
    return result


def get_pid(name: str, logger=None) -> int | None:
    """Return the PID of process 'name'."""
    logger = logger or get_caller_logger()
    logger.debug(f"Getting PID for process name: {name}")
    proc = get_proc(name)
    result = proc.pid if proc else None
    logger.debug(f"PID for '{name}': {result}")
    return result


def start_proc(
    cmd: Union[str, List[str]],
    disown: bool = False,
    background: bool = False,
    dev_null_stdout: bool = False,
    dev_null_stderr: bool = False,
    shell: bool = False,
    logger=None,
    **kwargs,
) -> bool:
    """Start a process and return True if successful False otherwise."""
    logger = logger or get_caller_logger()
    logger.debug(
        f"Starting process with cmd: {cmd}, disown: {disown}, background: {background}, shell: {shell}"
    )
    # Validate arguments
    if not cmd:
        logger.warning("Empty command provided to start_proc")
        return False

    # Prepare command
    if shell and isinstance(cmd, list):
        cmd = " ".join(cmd)
    elif not shell and isinstance(cmd, str):
        cmd = shlex.split(cmd)

    # Prepare stdout/stderr redirection
    stdout = subprocess.DEVNULL if dev_null_stdout else kwargs.pop("stdout", None)
    stderr = subprocess.DEVNULL if dev_null_stderr else kwargs.pop("stderr", None)

    # Setup process group for disowned/background processes
    start_new_session = disown or background

    # Exececutable name
    cmd_name = cmd[0] if isinstance(cmd, list) else cmd.split()[0]

    try:
        # Start the process
        logger.info(f"Starting process: {cmd_name}")
        subprocess.Popen(
            cmd,
            shell=shell,
            stdout=stdout,
            stderr=stderr,
            text=True,
            encoding="utf-8",
            start_new_session=start_new_session,
            **kwargs,
        )
        logger.info(f"Successfully started process: {cmd_name}")
        return True
    except FileNotFoundError as e:
        logger.error(f"Command not found '{cmd_name}', error: {e}")
        raise ProcessError(f"Command not found '{cmd_name}', error: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied while starting '{cmd_name}', error: {e}")
        raise ProcessError(f"Permission denied while starting '{cmd_name}', error: {e}")
    except Exception as e:
        logger.exception(
            f"Unexpected error while starting the process '{cmd_name}', error: {e}"
        )
        raise ProcessError(
            f"Unexpected error while starting the process '{cmd_name}', error: {e}"
        )


def kill_proc_tree(
    pid,
    sig=signal.SIGTERM,
    include_parent=True,
    timeout=None,
    logger=None,
) -> tuple[Iterable[psutil.Process], Iterable[psutil.Process]]:
    """Kill a process tree (including grandchildren) and return (gone, alive)."""
    logger = logger or get_caller_logger()
    logger.debug(
        f"Killing process tree for PID {pid} with signal {sig}, include_parent: {include_parent}, timeout: {timeout}"
    )
    if pid == os.getpid():
        logger.error("Attempted to kill own process")
        raise RuntimeError("won't kill myself")

    try:
        parent = psutil.Process(pid)
        logger.debug(f"Found parent process {pid}: {parent.name()}")
    except psutil.NoSuchProcess:
        logger.warning(f"Process {pid} does not exist")
        return ((), ())

    children = parent.children(recursive=True)
    logger.debug(f"Found {len(children)} child processes")
    if include_parent:
        children.append(parent)
        logger.debug("Including parent process in kill list")

    for p in children:
        try:
            p.send_signal(sig)
            logger.debug(f"Sent signal {sig} to process {p.pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logger.debug(f"Could not send signal to process {p.pid}")

    gone, alive = psutil.wait_procs(children, timeout=timeout)
    logger.info(f"Process tree kill completed. Gone: {len(gone)}, Alive: {len(alive)}")
    return (gone, alive)


def kill_proc(pid: int, logger=None) -> None:
    """Force kill a process by PID. Raises ProcessNotKilled on failure."""
    logger = logger or get_caller_logger()
    logger.info(f"Force killing process with PID: {pid}")
    if pid == os.getpid():
        logger.error("Attempted to kill own process")
        raise RuntimeError("won't kill myself")

    if not psutil.pid_exists(pid):
        logger.warning(f"Process {pid} does not exist, nothing to kill")
        return

    try:
        process = psutil.Process(pid)
        logger.debug(f"Sending SIGKILL to process {pid}")
        process.send_signal(signal.SIGKILL)
        try:
            process.wait(timeout=1)
            logger.info(f"Successfully killed process {pid}")
        except psutil.TimeoutExpired as e:
            logger.warning(
                f"SIGKILL timed out for process {pid}, attempting kill_proc_tree"
            )
            try:
                kill_proc_tree(pid, sig=signal.SIGKILL, include_parent=True)
            except Exception:
                logger.exception(f"Error in kill_proc_tree for process {pid}")
                pass
            # Raise if still active
            logger.error(f"Process {pid} still alive after SIGKILL and kill_proc_tree")
            raise ProcessNotKilled(pid, f"SIGKILL timed out: {e}")
    except psutil.NoSuchProcess:
        logger.warning(f"Process {pid} no longer exists")
        return
    except psutil.AccessDenied as e:
        logger.error(f"Permission denied when sending SIGKILL to process {pid}: {e}")
        raise ProcessNotKilled(pid, f"Permission denied when sending SIGKILL: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error when killing process {pid}: {e}")
        raise ProcessNotKilled(pid, f"Unexpected error when killing: {e}")


def term_proc(pid: int, timeout: float, logger=None) -> None:
    """Terminate a process gracefully, escalate to kill on timeout.
    Raises ProcessNotKilled on failure.
    """
    logger = logger or get_caller_logger()
    logger.info(f"Terminating process {pid} gracefully with timeout {timeout}")
    if pid == os.getpid():
        logger.error("Attempted to terminate own process")
        raise RuntimeError("won't terminate myself")

    if not psutil.pid_exists(pid):
        logger.warning(f"Process {pid} does not exist, nothing to terminate")
        return

    try:
        process = psutil.Process(pid)
        logger.debug(f"Sending SIGTERM to process {pid}")
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=timeout)
            logger.info(f"Successfully terminated process {pid} with SIGTERM")
            return
        except psutil.TimeoutExpired:
            logger.warning(
                f"SIGTERM timed out for process {pid}, escalating to SIGKILL"
            )
            # Escalate to SIGKILL
            try:
                process.send_signal(signal.SIGKILL)
                process.wait(timeout=timeout)
                logger.info(
                    f"Successfully killed process {pid} with SIGKILL after timeout"
                )
                return
            except psutil.TimeoutExpired as e:
                logger.error(
                    f"Process {pid} still alive after SIGTERM and SIGKILL: {e}"
                )
                raise ProcessNotKilled(
                    pid, f"Timed out after SIGTERM then SIGKILL: {e}"
                )
            except psutil.AccessDenied as e:
                logger.error(
                    f"Permission denied escalating to SIGKILL for process {pid}: {e}"
                )
                raise ProcessNotKilled(
                    pid, f"Permission denied escalating to SIGKILL: {e}"
                )
    except psutil.NoSuchProcess:
        logger.warning(f"Process {pid} no longer exists")
        return
    except psutil.AccessDenied as e:
        logger.error(f"Permission denied sending SIGTERM to process {pid}: {e}")
        raise ProcessNotKilled(pid, f"Permission denied sending SIGTERM: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error terminating process {pid}: {e}")
        raise ProcessNotKilled(pid, f"Unexpected error terminating process: {e}")


def send_signal(pid: int, sig, logger=None) -> bool:
    """Send a signal to a process.
    Returns True if successful, False if process doesn't exist or can't be signaled."""
    logger = logger or get_caller_logger()
    logger.debug(f"Sending signal {sig} to process {pid}")
    try:
        psutil.Process(pid).send_signal(sig)
        logger.debug(f"Successfully sent signal {sig} to process {pid}")
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        logger.warning(
            f"Failed to send signal {sig} to process {pid} (process doesn't exist or access denied)"
        )
        return False


def is_running(name: str, logger=None) -> bool:
    """Returns True if process 'name' is running, False otherwise"""
    logger = logger or get_caller_logger()
    logger.debug(f"Checking if process '{name}' is running")
    proc = get_proc(name)
    if not proc:
        logger.debug(f"Process '{name}' not found")
        return False
    try:
        result = proc.is_running()
        logger.debug(f"Process '{name}' is running: {result}")
        return result
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        logger.debug(f"Process '{name}' is no longer running or is a zombie")
        return False


class Process:
    """Base class for a named process."""

    def __init__(self, name: str, logger):
        self.name = name
        self.logger = logger
        self.logger.debug(f"Initializing Process instance for '{name}'")
        self.pid = get_pid(self.name, logger=self.logger)

    def is_running(self) -> bool:
        """Check if the process is running."""
        return is_running(self.name)

    def _refresh_pid(self) -> None:
        self.logger.debug(f"Refreshing PID for '{self.name}'")
        self.pid = get_pid(self.name, logger=self.logger)
        self.logger.debug(f"Current PID for '{self.name}': {self.pid}")

    def kill(self) -> bool:
        self.logger.debug(f"Killing {self.name}...")

        self._refresh_pid()
        if not self.pid:
            self.logger.info(f"{self.name} is not running, skipping to kill...")
            return True

        try:
            kill_proc(self.pid, logger=self.logger)
            time.sleep(0.05)
            self._refresh_pid()
            if self.pid and psutil.pid_exists(self.pid):
                self.logger.error(f"Failed to kill {self.name} (pid {self.pid})")
                return False
            self.logger.info(f"{self.name} killed.")
            return True
        except ProcessNotKilled as e:
            self.logger.error(f"Failed to kill process {self.name}: {e}")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error killing {self.name}: {e}")
            return False

    def start(self):
        """Start the process."""
        raise NotImplementedError("Subclasses must implement the start method.")

    def reload(self):
        """Reload the process."""
        if self.is_running():
            if not self.kill():
                self.logger.info(f"{self.name} failed to reload. Unable to kill...")
                return
            time.sleep(0.2)
            self.start()
            self.logger.info(f"{self.name} reloaded.")
        else:
            self.logger.info(f"{self.name} is not running. Starting it now...")
            self.start()

    def send_signal(self, sig) -> bool:
        """Send the signal 'sig' to the process"""
        self.logger.debug(f"Sending signal {sig} to process '{self.name}'")
        self._refresh_pid()

        if not self.pid:
            self.logger.info(
                f"'{self.name}' is not running, skipping to send signal '{sig}'..."
            )
            return True

        if not send_signal(self.pid, sig, logger=self.logger):
            self.logger.info(f"Failed to send signal '{sig}'")
            return False

        self.logger.debug(f"Successfully sent signal {sig} to process '{self.name}'")
        return True
