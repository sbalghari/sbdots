import os
import re
import threading
import subprocess
import concurrent.futures
from pathlib import Path

from utils.logger import Logger
from utils.paths import SBDOTS_LOG_DIR, SBDOTS_CONFIG_DIR
from library import path_lexists, Notification


class OnWallpaperChange:
    def __init__(self, *args):
        # Create logfile
        self.logfile: Path = SBDOTS_LOG_DIR / "on_wallpaper_change.log"
        self.logfile.parent.mkdir(parents=True, exist_ok=True)
        self.logfile.unlink(missing_ok=True)

        # Setup logging
        self.logger = Logger(log_file=self.logfile)

        # Paths
        self.home = Path.home()
        self.config_dir = SBDOTS_CONFIG_DIR

        # Validate args
        if not args:
            self.logger.error("No wallpaper path given.")
            self._notify_action_failed()

        self.wallpaper_path = Path(args[1])

        if not path_lexists(self.wallpaper_path):
            self.logger.error(f"Invalid wallpaper path: {self.wallpaper_path}")
            self._notify_action_failed()

    def _run_command(self, cmd) -> bool:
        """Run a shell command and return True on success, False on failure."""
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(
                f"Command <{cmd}> failed\nstderr: {e.stderr}\nstdout: {e.stdout}"
            )
            return False

    def _notify_action_failed(self):
        """Show a desktop notification when the action fails."""
        try:
            self._run_command(
                f'notify-send "SBDots Actions" '
                f'"Post wallpaper change script failed. Check {self.logfile} for details."'
            )
        finally:
            raise RuntimeError("Post wallpaper change script failed.")

    def _validate_color(self, hex_color: str) -> bool:
        """Validate hex color format."""
        pattern = r"^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
        return re.match(pattern, hex_color) is not None

    def _hex_to_argb(self, hex_color: str) -> str:
        """Convert hex color (#rrggbb) to ARGB format (0xaarrggbb)."""
        hex_color = hex_color.lstrip("#")

        # Handle 3-digit hex colors
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])

        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: {hex_color}")

        if not self._validate_color(hex_color):
            raise ValueError(f"Invalid hex color format: {hex_color}")

        rr, gg, bb = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        return f"0xb3{rr}{gg}{bb}"

    def generate_pywal_colors(self) -> bool:
        self.logger.debug("Generating pywal colors...")
        if not self._run_command(f'wal -i "{self.wallpaper_path}"'):
            self.logger.error("Failed to generate pywal colors.")
            return False
        return True

    def _create_blurred_image(self) -> bool:
        """Internal method to create blurred wallpaper image."""
        target_dir = self.config_dir / "wallpaper_variants"
        target_dir.mkdir(parents=True, exist_ok=True)
        output_image = target_dir / "blurred.jpg"

        cmd = f'magick "{self.wallpaper_path}" -blur 0x10 "{output_image}"'

        if not self._run_command(cmd):
            self.logger.error("Failed to create blurred wallpaper.")
            return False
        return True

    def store_blurred_wallpaper(self) -> bool:
        """Create blurred wallpaper with timeout handling."""

        self.logger.debug("Creating blurred wallpaper...")

        try:
            # Use ThreadPoolExecutor for better resource management
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._create_blurred_image)
                return future.result(timeout=5)
        except concurrent.futures.TimeoutError:
            self.logger.warning(f"Blur operation timed out after {5} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error in blur operation: {e}")
            return False

    def update_hyprland_colors(self) -> bool:
        self.logger.debug("Updating Hyprland colors...")

        pywal_colors_css = self.home / ".cache" / "wal" / "colors.css"
        if not path_lexists(pywal_colors_css):
            self.logger.error(f"Pywal colors.css not found: {pywal_colors_css}")
            return False

        try:
            with open(pywal_colors_css, "r") as f:
                content = f.read()

            fg_match = re.search(r"--color11:\s*(#[0-9a-fA-F]+)", content)
            bg_match = re.search(r"--color0:\s*(#[0-9a-fA-F]+)", content)

            if not fg_match or not bg_match:
                self.logger.error("Failed to extract colors from pywal CSS.")
                return False

            fg_hex = fg_match.group(1)
            bg_hex = bg_match.group(1)

            # Validate colors before conversion
            if not (self._validate_color(fg_hex) and self._validate_color(bg_hex)):
                self.logger.error("Invalid color format extracted from pywal CSS")
                return False

            fg_argb = self._hex_to_argb(fg_hex)
            bg_argb = self._hex_to_argb(bg_hex)

            self.logger.info(f"Foreground: {fg_argb}")
            self.logger.info(f"Background: {bg_argb}")

            colors_conf = self.home / ".config" / "hypr" / "configs" / "colors.conf"
            colors_conf.parent.mkdir(parents=True, exist_ok=True)

            with open(colors_conf, "w") as f:
                f.write(f"$fg = {fg_argb}\n$bg = {bg_argb}\n")

        except Exception as e:
            self.logger.error(f"Error updating Hyprland colors: {e}")
            return False

        return True

    def reload_services(self) -> bool:
        self.logger.debug("Reloading services...")

        cmds = [
            "swaync-client -rs",
            "bash $HOME/.config/hypr/services/waybar.sh -r",
            "hyprctl reload",
        ]
        all_success = True

        for cmd in cmds:
            result = self._run_command(cmd)
            if not result:
                self.logger.error(f"Failed to run command: {cmd}")
                all_success = False
                # Continue with other services
                continue

        return all_success

    def main(self):
        """Main sequence execution."""
        if not os.path.exists(self.wallpaper_path):
            self.logger.error(f"Wallpaper path does not exist: {self.wallpaper_path}")
            self._notify_action_failed()

        blur_thread = None
        try:
            with Notification(
                "SBDots - Actions", "Executing post wallpaper change scripts."
            ) as n:
                total_steps = 5
                progress_step = 100 // total_steps
                current_progress = 0

                # Step 1: start blur in background
                self.logger.debug(
                    "Starting blurred wallpaper generation in background thread..."
                )
                blur_thread = threading.Thread(
                    target=self.store_blurred_wallpaper, daemon=True
                )
                blur_thread.start()

                # Step 2: generate pywal colors 
                current_progress += progress_step
                n.update(
                    body_text="Generating pywal colors from the wallpaper...",
                    progress_value=current_progress,
                )
                if not self.generate_pywal_colors():
                    self._notify_action_failed()

                # Step 3: update Hyprland colors
                current_progress += progress_step
                n.update(
                    body_text="Updating Hyprland border colors...",
                    progress_value=current_progress,
                )
                if not self.update_hyprland_colors():
                    self._notify_action_failed()

                # Step 4: reload services
                current_progress += progress_step
                n.update(
                    body_text="Reloading services...", progress_value=current_progress
                )
                if not self.reload_services():
                    self._notify_action_failed()

                # Step 5: wait for blur thread
                current_progress += progress_step
                n.update(
                    body_text="Creating blurred variant of the wallpaper...",
                    progress_value=current_progress,
                )
                blur_thread.join(timeout=2)
                if blur_thread.is_alive():
                    self.logger.info(
                        "Blur operation still running in background - continuing without waiting"
                    )
                else:
                    self.logger.debug("Blur operation completed successfully")

                # Final success notification
                n.update(
                    body_text="Post wallpaper change scripts executed successfully.",
                    progress_value=100,
                )
                self.logger.info("Wallpaper change actions completed successfully")

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            self._notify_action_failed()

        finally:
            # Ensure background thread is properly cleaned up
            if blur_thread and blur_thread.is_alive():
                self.logger.debug("Waiting for blur thread to finish...")
                blur_thread.join(timeout=2)
                if blur_thread.is_alive():
                    self.logger.warning("Blur thread still running after final timeout")
