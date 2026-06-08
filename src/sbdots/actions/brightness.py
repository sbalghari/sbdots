from typing import Literal
from subprocess import CalledProcessError

from sbdots.library.commands import check_output, run_command
from sbdots.library.command import notify_send
from ._base import BaseAction


class Brightness(BaseAction):
    def main(self) -> None:

        delta = self.args[0].lower()
        delta_value = self.args[1]

        try:
            delta_value = int(delta_value)
        except ValueError:
            self.send(
                {"status": "Error", "stderr": f"expected <int>, got {type(delta)}"}
            )
            return

        if not (0 <= delta_value <= 100):
            self.send(
                {
                    "status": "Error",
                    "stderr": f"expected value between 0 and 100, got {delta_value}",
                }
            )
            return

        # Do nothing if brightness is already 100% and try to increase or 0% and try to decrese
        curr = self.get_current()
        if (curr == 100 and delta == "up") or (curr == 0 and delta == "down"):
            return

        if delta == "down":
            self.update("-", delta_value)
        elif delta == "up":
            self.update("+", delta_value)
        else:
            self.send(
                {
                    "status": "Error",
                    "stderr": f"expected literal 'up' or 'down', got '{delta}' of type {type(delta)}",
                }
            )
            return

    def notify(self, value: int) -> None:
        icons = [
            (0, "󰃞"),
            (33, "󰃟"),
            (66, "󰃠"),
            (100, "󰃡"),
        ]

        icon = next(i for threshold, i in icons if value <= threshold)

        notify_send(
            f"{icon}  {value}%",
            urgency="low",
            expire_time=1000,
            progress_value=value,
            sync_tag="brightness-notification",
        )

    def update(self, delta: Literal["-"] | Literal["+"], delta_value: int) -> None:
        try:
            run_command(["brightnessctl", "set", f"{delta_value}%{delta}"], check=True)
            self.notify(self.get_current())

        except CalledProcessError as e:
            self.send(
                {
                    "status": "Error",
                    "command": e.cmd,
                    "returncode": e.returncode,
                    "stdout": e.stdout or "",
                    "stderr": e.stderr or "",
                }
            )

    def get_current(self) -> int:
        # Cmd 'brightnessctl -m' returns something like this <amdgpu_bl1,backlight,49961,80%,62451>
        # so, output will store ['amdgpu_bl1', 'backlight', '49961', '80%', '62451']
        output: str = check_output(["brightnessctl", "-m"]).strip().split(",")

        # Return the 4th item with '%' removed
        return int(output[3].strip("%"))
