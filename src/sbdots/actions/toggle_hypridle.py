import logging

from sbdots.library.procs_utils import (
    is_running,
    get_pid,
    term_proc,
    start_proc,
)
from sbdots.library.logger import setup_actions_state
from sbdots.library.exceptions import ProcessError
from ._base import BaseAction

setup_actions_state(__name__)
logger = logging.getLogger(__name__)


class ToggleHypridle(BaseAction):
    def main(self):
        if is_running("hypridle"):
            logger.debug("Hypridle is running, toggling it off...")
            if pid := get_pid("hypridle"):
                try:
                    term_proc(pid, 0.2, logger=logger)
                except ProcessError as e:
                    logger.exception("Failed to kill 'hypridle'.", exc_info=e)
                logger.info("Hypridle toggled off successfully.")
                self.send({"status": "OFF"})
        else:
            logger.debug("Hypridle is not running, toggling it on...")
            try:
                start_proc("hypridle", disown=True, dev_null_stdout=True, logger=logger)

            except RuntimeError as e:
                logger.exception("'hypridle' failed to start: ", exc_info=e)
            self.send({"status": "ONN"})
