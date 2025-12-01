from pathlib import Path

from library import is_running, get_pid, term_proc, start_proc
from utils.logger import Logger
from utils.paths import SBDOTS_LOG_DIR
from utils.errors import ProcessNotKilled


class ToggleHypridleProcs:
    def __init__(self, conn, *args) -> None:
        # Create logfile and setup logging
        self.logfile: Path = SBDOTS_LOG_DIR / "hypridle.log"
        self.logfile.parent.mkdir(parents=True, exist_ok=True)
        self.logfile.unlink(missing_ok=True)
        self.logger = Logger(log_file=self.logfile)

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
                    f"{self.procs_name} failed to start: ", exec_info=e
                )
                return
            self.conn("hypridle: on.")
