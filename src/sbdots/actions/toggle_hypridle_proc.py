import logging

from sbdots.core.process import is_running, get_pid, term_proc, start_proc
from sbdots.utils.logger import setup_actions_state
from sbdots.utils.exceptions import ProcessNotKilled


class ToggleHypridleProc:
    def __init__(self, conn, *args) -> None:
        # Setup logging
        self.logger_name = self.__class__.__name__
        setup_actions_state(self.logger_name)
        self.logger = logging.getLogger(self.logger_name)

        # Socket connection
        self.conn = conn

        self.procs_name = "hypridle"

    def send(self, msg: str) -> None:
        try:
            self.conn.sendall(b"\n")
            self.conn.sendall((msg + "\n").encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def main(self):
        if is_running(self.procs_name):
            self.logger.debug("Hypridle is running, toggling it off...")
            if pid := get_pid(self.procs_name):
                try:
                    term_proc(pid, 0.5)
                except ProcessNotKilled as e:
                    self.logger.exception(f"Failed to kill {self.procs_name}: {e}")
                    return
                self.conn("hypridle: off.")
                self.logger.info("Hypridle toggled off successfully.")
        else:
            self.logger.debug("Hypridle is not running, toggling it on...")
            try:
                start_proc(self.procs_name)

            except RuntimeError as e:
                self.logger.exception(
                    f"{self.procs_name} failed to start: ", exc_info=e
                )
                return
            self.conn("hypridle: on.")
