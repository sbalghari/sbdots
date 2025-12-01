import os
import psutil
import signal
import time
from typing import Iterable
from utils.errors import ProcessNotKilled

from typing import List, Optional, Union


def get_procs(name: str) -> List[psutil.Process]:
    """Return all processes matching 'name'."""
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
    return procs


def get_proc(name: str) -> Optional[psutil.Process]:
    """Return the first process matching 'name'."""
    proc = get_procs(name)
    return proc[0] if proc else None


def get_pid(name: str) -> int | None:
    """Return the PID of process 'name'."""
    proc = get_proc(name)
    return proc.pid if proc else None


def start_proc(cmd: Union[str, List[str]]) -> int:
    """Start a process using psutil.Popen and return its PID."""
    # Normalize the command to extract executable name
    if isinstance(cmd, str):
        exec_name = cmd.strip().split()[0]
        popen_cmd = cmd
    elif isinstance(cmd, (list, tuple)):
        if not cmd:
            raise ValueError("Command list cannot be empty")
        exec_name = cmd[0]
        popen_cmd = list(cmd)
    else:
        raise TypeError("Command must be a string or list")

    if is_running(exec_name):
        raise RuntimeError(f"Process '{exec_name}' is already running")

    try:
        process = psutil.Popen(popen_cmd)
        return process.pidcmd
    except Exception as e:
        raise RuntimeError(f"Failed to start '{exec_name}': {e}")


def kill_proc_tree(
    pid,
    sig=signal.SIGTERM,
    include_parent=True,
    timeout=None,
) -> tuple[Iterable[psutil.Process], Iterable[psutil.Process]]:
    """Kill a process tree (including grandchildren) and return (gone, alive)."""
    if pid == os.getpid():
        raise RuntimeError("won't kill myself")

    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return ((), ())

    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)

    for p in children:
        try:
            p.send_signal(sig)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    gone, alive = psutil.wait_procs(children, timeout=timeout)
    return (gone, alive)


def kill_proc(pid: int) -> None:
    """Force kill a process by PID. Raises ProcessNotKilled on failure."""
    if pid == os.getpid():
        raise RuntimeError("won't kill myself")

    if not psutil.pid_exists(pid):
        return

    try:
        process = psutil.Process(pid)
        process.send_signal(signal.SIGKILL)
        try:
            process.wait(timeout=1)
        except psutil.TimeoutExpired as e:
            try:
                kill_proc_tree(pid, sig=signal.SIGKILL, include_parent=True)
            except Exception:
                pass
            # Raise if still active
            raise ProcessNotKilled(pid, f"SIGKILL timed out: {e}")
    except psutil.NoSuchProcess:
        return
    except psutil.AccessDenied as e:
        raise ProcessNotKilled(pid, f"Permission denied when sending SIGKILL: {e}")
    except Exception as e:
        raise ProcessNotKilled(pid, f"Unexpected error when killing: {e}")


def term_proc(pid: int, timeout: float) -> None:
    """Terminate a process gracefully, escalate to kill on timeout.
    Raises ProcessNotKilled on failure.
    """
    if pid == os.getpid():
        raise RuntimeError("won't terminate myself")

    if not psutil.pid_exists(pid):
        return

    try:
        process = psutil.Process(pid)
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=timeout)
            return
        except psutil.TimeoutExpired:
            # Escalate to SIGKILL
            try:
                process.send_signal(signal.SIGKILL)
                process.wait(timeout=timeout)
                return
            except psutil.TimeoutExpired as e:
                raise ProcessNotKilled(
                    pid, f"Timed out after SIGTERM then SIGKILL: {e}"
                )
            except psutil.AccessDenied as e:
                raise ProcessNotKilled(
                    pid, f"Permission denied escalating to SIGKILL: {e}"
                )
    except psutil.NoSuchProcess:
        return
    except psutil.AccessDenied as e:
        raise ProcessNotKilled(pid, f"Permission denied sending SIGTERM: {e}")
    except Exception as e:
        raise ProcessNotKilled(pid, f"Unexpected error terminating process: {e}")


def send_signal(pid: int, sig) -> bool:
    """Send a signal to a process.
    Returns True if successful, False if process doesn't exist or can't be signaled."""
    try:
        psutil.Process(pid).send_signal(sig)
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def is_running(name: str) -> bool:
    """Returns True if process 'name' is running, False otherwise"""
    proc = get_proc(name)
    if not proc:
        return False
    try:
        return proc.is_running()
    except (psutil.NoSuchProcess, psutil.ZombieProcess):
        return False


class Process:
    """Base class for a named process."""

    def __init__(self, name: str, logger):
        self.name = name
        self.logger = logger
        self.pid = get_pid(self.name)

    def is_running(self) -> bool:
        """Check if the process is running."""
        return is_running(self.name)

    def _refresh_pid(self) -> None:
        self.pid = get_pid(self.name)

    def kill(self) -> bool:
        self.logger.debug(f"Killing {self.name}...")

        self._refresh_pid()
        if not self.pid:
            self.logger.info(f"{self.name} is not running, skipping to kill...")
            return True

        try:
            kill_proc(self.pid)
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
        self._refresh_pid()
        
        if not self.pid:
            self.logger.info(f"'{self.name}' is not running, skipping to send signal '{sig}'...")
            return True
        
        if not send_signal(self.pid, sig):
            self.logger.info(f"Failed to send signal '{sig}'")
            return False
            
        return True
