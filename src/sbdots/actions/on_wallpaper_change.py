import logging
import subprocess
import shutil
from pathlib import Path

from sbdots.library.logger import setup_actions_state
from sbdots.library.fs_ops import path_lexists
from sbdots.library.notify import Notification, notify_send
from sbdots.library.command import MatugenImage
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
                title="SBDots-Actions",
                message=f"action: 'on_wallpaper_change' has failed, check logs at '{SBDOTS_STATE_DIR}'",
                urgency="critical",
            )
        finally:
            raise RuntimeError("Post wallpaper change script failed.")

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
            with Notification(
                "SBDots - Actions", "Executing post wallpaper change scripts."
            ) as n:
                total_steps = 3
                progress_step = 100 // total_steps
                current_progress = 0

                # Step: 1 - copy wallpaper
                current_progress += progress_step
                n.update(
                    body_text="Updating cached wallpaper...",
                    progress_value=current_progress,
                )

                cached_wallpaper = Path.home() / ".cache" / "current.wall"
                cached_wallpaper.parent.mkdir(parents=True, exist_ok=True)

                shutil.copy2(
                    self.wallpaper_path,
                    cached_wallpaper,
                )

                logger.debug(f"Copied wallpaper to cache: {cached_wallpaper}")

                # Step: 2 - start matugen op
                current_progress += progress_step
                n.update(
                    body_text="Generating matugen colors...",
                    progress_value=current_progress,
                )

                cmd = MatugenImage(logger)._build_command(
                    image_path=self.wallpaper_path
                )
                self.send({"cmd": cmd})
                matugen_proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                logger.debug("Started generating matugen colors")

                # Step: 3 - wait for matugen
                current_progress += progress_step
                matugen_stdout, matugen_stderr = matugen_proc.communicate()
                if matugen_proc.returncode != 0:
                    msg = f"Matugen operation failed\nstdout: {matugen_stdout}\nstderr: {matugen_stderr}"
                    logger.error(msg)
                    self.send({"error": msg})
                    self._notify_action_failed()

                logger.debug("Matugen operation completed successfully")

                # Final success notification
                n.update(
                    body_text="Post wallpaper change scripts executed successfully.",
                    progress_value=100,
                )
                logger.info("Wallpaper change actions completed successfully")

        except Exception as e:
            logger.exception("Unexpected error:")
            self.send({"error": str(e)})
            self._notify_action_failed()
