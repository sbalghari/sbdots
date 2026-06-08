import logging
import subprocess
import shutil
from pathlib import Path

from sbdots.library.logger import setup_actions_state
from sbdots.library.fs_ops import path_lexists
from sbdots.library.command import MatugenImage, notify_send
from sbdots.constants import SBDOTS_STATE_DIR
from ._base import BaseAction


setup_actions_state(__name__)
logger = logging.getLogger(__name__)


class OnWallpaperChange(BaseAction):
    def _run_command(self, cmd) -> bool:
        """Run a shell command and return True on success, False on failure."""
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Command <{cmd}> failed\nstderr: {e.stderr}\nstdout: {e.stdout}"
            )
            return False

    def _notify_action_failed(self):
        """Show a desktop notification when the action fails."""
        try:
            notify_send(
                "SBDots-Actions",
                body=f"action: 'on_wallpaper_change' has failed, check logs at '{SBDOTS_STATE_DIR}'",
                urgency="critical",
                icon="sbdots",
            )
        finally:
            raise RuntimeError("Post wallpaper change script failed.")

    def _notify_progress(self, progress: int, text: str) -> None:
        notify_send(
            "SBDots - Actions",
            body=text,
            urgency="low",
            progress_value=progress,
            sync_tag="on-wallpaper-change-notfication",
            icon="sbdots",
        )

    def main(self):
        # Validate args
        if len(self.args) < 1:
            logger.error("No wallpaper path given.")
            self.send({"error": "no wallpaper path given"})
            self._notify_action_failed()

        # Validate wallpaper path
        self.wallpaper_path = Path(self.args[0])
        if not path_lexists(self.wallpaper_path):
            logger.error(f"Invalid wallpaper path: {self.wallpaper_path}")
            self._notify_action_failed()

        try:
            self._notify_progress(
                text="Executing post wallpaper change scripts.", progress=0
            )

            # Step: 1 - start matugen color generation
            self._notify_progress(text="Generating matugen colors...", progress=60)

            cmd = MatugenImage(logger)._build_command(image_path=self.wallpaper_path)
            self.send({"cmd": cmd})
            matugen_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            logger.debug("Started generating matugen colors")

            # Step: 2 - cache wallpaper
            self._notify_progress(text="Updating cached wallpaper...", progress=30)

            cached_wallpaper = Path.home() / ".cache" / "current.wall"
            cached_wallpaper.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(
                self.wallpaper_path,
                cached_wallpaper,
            )

            logger.debug(f"Copied wallpaper to cache: {cached_wallpaper}")

            # Step: 3 - wait for matugen
            self._notify_progress(
                text="Waiting for matugen to finish generating colors...", progress=90
            )
            matugen_stdout, matugen_stderr = matugen_proc.communicate()
            if matugen_proc.returncode != 0:
                msg = f"Matugen operation failed\nstdout: {matugen_stdout}\nstderr: {matugen_stderr}"
                logger.error(msg)
                self.send({"error": msg})
                self._notify_action_failed()

            logger.debug("Matugen operation completed successfully")

            # Final success notification
            self._notify_progress(
                text="Post wallpaper change scripts executed successfully.",
                progress=100,
            )
            logger.info("Wallpaper change actions completed successfully")

        except Exception as e:
            logger.exception("Unexpected error:")
            self.send({"error": str(e)})
            self._notify_action_failed()
