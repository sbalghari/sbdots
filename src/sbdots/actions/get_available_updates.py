import shutil
import logging

from sbdots.library.logger import setup_actions_state
from sbdots.library.commands import check_output
from ._base import BaseAction

setup_actions_state(__name__)
logger = logging.getLogger(__name__)


class GetAvailableUpdates(BaseAction):
    def main(self) -> None:
        total_updates, pacman_updates, aur_updates, flatpak_updates = (
            self._calculate_updates()
        )
        css_class = self._determine_css_class(total_updates)

        if total_updates <= 0:
            data = {"text": "", "class": "none"}
        else:
            data = {
                "text": f" {total_updates}",
                "alt": str(total_updates),
                "tooltip": f"PACMAN updates: {pacman_updates} \nAUR updates: {aur_updates} \nFlatpak updates: {flatpak_updates}",
                "class": css_class,
            }

        self.send(data)

    def _calculate_updates(self):
        total_updates: int = 0
        pacman_updates: str | int = self._get_pacman_updates()
        total_updates += pacman_updates if isinstance(pacman_updates, int) else 0

        aur_updates: str | int = self._get_aur_updates()
        total_updates += aur_updates if isinstance(aur_updates, int) else 0

        flatpak_updates: str | int = self._get_flatpak_updates()
        total_updates += flatpak_updates if isinstance(flatpak_updates, int) else 0

        return total_updates, pacman_updates, aur_updates, flatpak_updates

    def _get_pacman_updates(self):
        if shutil.which("checkupdates"):
            try:
                pacman_updates_raw = check_output(
                    ["checkupdates"],
                ).strip()
                return len(pacman_updates_raw.split("\n")) if pacman_updates_raw else 0
            except FileNotFoundError:
                return 0
        else:
            return "'pacman-contrib' Not-installed"

    def _get_aur_updates(self):
        if shutil.which("yay") or shutil.which("paru"):
            if shutil.which("aur-check-updates"):
                try:
                    aur_updates_raw = check_output(
                        ["aur-check-updates"],
                    ).strip()
                    aur_updates = (
                        len(aur_updates_raw.split("\n")) if aur_updates_raw else 0
                    )
                    return (
                        aur_updates - 2
                    )  # first 2 lines are aur-check-updates's stdout
                except FileNotFoundError:
                    return 0
            else:
                return "'aur-check-updates' Not-installed"
        else:
            return "'yay' | 'paru' Not-installed"

    def _get_flatpak_updates(self):
        if shutil.which("flatpak"):
            try:
                flatpak_updates_raw = check_output(
                    ["flatpak", "remote-ls", "--updates"],
                ).strip()
                return (
                    len(flatpak_updates_raw.split("\n")) if flatpak_updates_raw else 0
                )
            except FileNotFoundError:
                return 0
        else:
            return "'flatpak' Not-installed"

    def _determine_css_class(self, total_updates):
        threshold_green = 1
        threshold_yellow = 25
        threshold_red = 50

        css_class = "none"
        if total_updates >= threshold_green:
            css_class = "green"
        if total_updates >= threshold_yellow:
            css_class = "yellow"
        if total_updates >= threshold_red:
            css_class = "red"
        return css_class
