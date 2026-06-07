from typing import Literal
from subprocess import CalledProcessError

from sbdots.library.commands import check_output, run_command
from ._base import BaseAction


class Volume(BaseAction):
    def main(self) -> None:

        delta = self.args[0].lower()

        if delta != "toggle":
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

        # Do nothing if volume is already 100% and try to increase or 0% and try to decrease
        curr = self.get_current()
        if (curr == 100 and delta == "up") or (curr == 0 and delta == "down"):
            return

        if delta == "toggle":
            self.toggle_mute()
        elif delta == "down":
            self.update("-", delta_value)
            self.notify(curr - delta_value)
        elif delta == "up":
            self.update("+", delta_value)
            self.notify(curr + delta_value)
        else:
            self.send(
                {
                    "status": "Error",
                    "stderr": f"expected literal 'up', 'down', or 'toggle', got '{delta}' of type {type(delta)}",
                }
            )
            return

    def notify(self, value: int) -> None:
        # Check if muted
        is_muted = self.is_muted()

        if is_muted:
            icon = "󰝟"  # muted icon
        else:
            icons = [
                (0, "󰝟"),
                (33, "󰕿"),
                (66, "󰖀"),
                (100, "󰕾"),
            ]
            icon = next(i for threshold, i in icons if value <= threshold)

        run_command(
            [
                "notify-send",
                f"{icon}  {value}%",
                "-a",
                "SBDOTS",
                "-u",
                "low",
                "-t",
                "1000",
                "-h",
                f"int:value:{value}",
                "-h",
                "string:x-canonical-private-synchronous:volume-notification",
            ]
        )

    def update(self, delta: Literal["-"] | Literal["+"], delta_value: int) -> None:
        try:
            if delta == "+":
                run_command(
                    [
                        "wpctl",
                        "set-volume",
                        "-l",
                        "1",
                        "@DEFAULT_AUDIO_SINK@",
                        f"{delta_value}%+",
                    ],
                    check=True,
                )
            else:  # delta == "-"
                run_command(
                    ["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{delta_value}%-"],
                    check=True,
                )
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
        # Get current volume from wpctl
        output: str = check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])

        # Parse volume (e.g., "Volume: 0.64" or "Volume: 0.64 [MUTED]")
        import re

        match = re.search(r"Volume:\s+([\d.]+)", output)
        if match:
            # Convert from decimal (0.00-1.00) to percentage (0-100)
            volume_decimal = float(match.group(1))
            return min(100, max(0, round(volume_decimal * 100)))

        return 0

    def is_muted(self) -> bool:
        """Check if the default audio sink is muted"""
        try:
            output: str = check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
            return "[MUTED]" in output
        except CalledProcessError:
            return False

    def toggle_mute(self) -> None:
        """Toggle mute state"""
        try:
            run_command(
                ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], check=True
            )

            # Send notification for mute/unmute
            is_muted = self.is_muted()
            current_vol = self.get_current()

            if is_muted:
                icon = "󰝟"
                vol_display = "Muted"
            else:
                icon = "󰕾"
                vol_display = f"{current_vol}%"

            run_command(
                [
                    "notify-send",
                    f"{icon}  {vol_display}",
                    "-a",
                    "SBDOTS",
                    "-u",
                    "low",
                    "-t",
                    "1000",
                    "-h",
                    "string:x-canonical-private-synchronous:volume-notification",
                ]
            )
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
