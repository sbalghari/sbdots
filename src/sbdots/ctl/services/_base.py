import psutil
import time

from sbdots.library.exceptions import ProcessNotKilled
from sbdots.library.procs_utils import (
    get_pid,
    is_running,
    kill_proc,
    send_signal,
)


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
            self.logger.info(
                f"{self.name} is not running, skipping to kill..."
            )
            return True

        try:
            kill_proc(self.pid, logger=self.logger)
            time.sleep(0.05)
            self._refresh_pid()
            if self.pid and psutil.pid_exists(self.pid):
                self.logger.error(
                    f"Failed to kill {self.name} (pid {self.pid})"
                )
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
        raise NotImplementedError(
            "Subclasses must implement the start method."
        )

    def reload(self):
        """Reload the process."""
        if self.is_running():
            if not self.kill():
                self.logger.info(
                    f"{self.name} failed to reload. Unable to kill..."
                )
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

        self.logger.debug(
            f"Successfully sent signal {sig} to process '{self.name}'"
        )
        return True
