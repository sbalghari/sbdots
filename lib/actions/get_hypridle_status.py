import json
from library import find_procs_by_name


class GetHypridleStatus:
    def __init__(self, conn, *args):
        self.conn = conn
        self.procs_name = "hypridle"

    def _is_running(self) -> bool:
        return bool(find_procs_by_name(self.procs_name))

    def send(self, data: dict) -> None:
        try:
            payload = json.dumps(data) + "\n"
            self.conn.sendall(b"\n")
            self.conn.sendall(payload.encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def main(self) -> None:
        if self._is_running():
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
