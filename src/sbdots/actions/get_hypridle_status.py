import logging
import json

from sbdots.utils.logger import setup_actions_state
from sbdots.core.process import is_running


class GetHypridleStatus:
    def __init__(self, conn, *args):
        # Setup logging
        self.logger_name = self.__class__.__name__
        setup_actions_state(self.logger_name)
        self.logger = logging.getLogger(self.logger_name)
        
        self.conn = conn
        self.procs_name = "hypridle"

    def send(self, data: dict) -> None:
        try:
            payload = json.dumps(data) + "\n"
            self.conn.sendall(b"\n")
            self.conn.sendall(payload.encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def main(self) -> None:
        if is_running(self.procs_name):
            self.send(
                {
                    "text": "On",
                    "class": "active",
                    "tooltip": "Screen locking active\nLeft: Deactivate\nRight: Lock Screen \nScreen will be locked after 5 minutes of inactivity.",
                }
            )
        else:
            self.send(
                {
                    "text": "Off",
                    "class": "notactive",
                    "tooltip": "Screen locking deactivated\nLeft: Activate\nRight: Lock Screen",
                }
            )
