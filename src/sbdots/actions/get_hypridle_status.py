# import logging

# from sbdots.library.logger import setup_actions_state
from sbdots.library.procs_utils import is_running
from ._base import BaseAction


# setup_actions_state(__name__)
# logger = logging.getLogger(__name__)


class GetHypridleStatus(BaseAction):
    def main(self) -> None:
        if is_running("hypridle"):
            data = {
                "text": "On",
                "class": "active",
                "tooltip": "Screen locking active\nLeft: Deactivate\nRight: Lock Screen \nScreen will be locked after 5 minutes of inactivity.",
            }

        else:
            data = {
                "text": "Off",
                "class": "notactive",
                "tooltip": "Screen locking deactivated\nLeft: Activate\nRight: Lock Screen",
            }

        self.send(data)
