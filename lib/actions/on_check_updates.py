import shutil
import subprocess
import json


class OnCheckUpdates:
    def __init__(self, conn, *args):
        self.conn = conn

    def main(self):
        # Define thresholds for color indicators
        threshold_none = 0
        threshold_green = 1
        threshold_yellow = 25
        threshold_red = 50

        # Updates counters
        total_updates: int = 0
        pacman_updates: str | int = 0
        aur_updates: str | int = 0
        flatpak_updates: str | int = 0

        # Calculate updates
        if shutil.which("checkupdates"):
            try:
                pacman_updates_raw = subprocess.run(
                    ["checkupdates"],
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                pacman_updates = (
                    len(pacman_updates_raw.split("\n")) if pacman_updates_raw else 0
                )
                total_updates += pacman_updates
            except FileNotFoundError:
                pacman_updates = 0
        else:
            pacman_updates = "'pacman-contrib' Not-installed"

        if shutil.which("yay") or shutil.which("paru"):
            if shutil.which("aur-check-updates"):
                try:
                    aur_updates_raw = subprocess.run(
                        ["aur-check-updates"],
                        capture_output=True,
                        text=True,
                    ).stdout.strip()
                    aur_updates = (
                        len(aur_updates_raw.split("\n")) if aur_updates_raw else 0
                    )
                    aur_updates -= 2  # first 2 lines are aur-check-updates's stdout
                    total_updates += aur_updates
                except FileNotFoundError:
                    aur_updates = 0
            else:
                aur_updates = "'aur-check-updates' Not-installed"
        else:
            aur_updates = "'yay' | 'paru' Not-installed"

        if shutil.which("flatpak"):
            try:
                flatpak_updates_raw = subprocess.run(
                    ["flatpak", "remote-ls", "--updates"],
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                flatpak_updates = (
                    len(flatpak_updates_raw.split("\n")) if flatpak_updates_raw else 0
                )
                total_updates += flatpak_updates
            except FileNotFoundError:
                flatpak_updates = 0

        else:
            flatpak_updates = "'flatpak' Not-installed"

        # Determine CSS class
        css_class = "none"
        if total_updates >= threshold_green:
            css_class = "green"
        if total_updates >= threshold_yellow:
            css_class = "yellow"
        if total_updates >= threshold_red:
            css_class = "red"

        # Output in JSON format
        if total_updates <= threshold_none:
            try:
                self.conn.sendall(b"\n")
                self.conn.sendall(
                    (json.dumps({"text": "", "class": "none"}) + "\n").encode("utf-8")
                )
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
        else:
            try:
                self.conn.sendall(b"\n")
                self.conn.sendall(
                    (
                        json.dumps(
                            {
                                "text": f" {total_updates}",
                                "alt": str(total_updates),
                                "tooltip": f"PACMAN updates: {pacman_updates} \nAUR updates: {aur_updates} \nFlatpak updates: {flatpak_updates}",
                                "class": css_class,
                            }
                        )
                        + "\n"
                    ).encode("utf-8")
                )
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
