from time import sleep
import subprocess
import shutil
from pathlib import Path

from utils.paths import USER_WALLPAPERS_DIR, SBDOTS_WALLPAPERS_DIR
from library.tui import print_header, Spinner, confirm, get_console, print_newline


class WallpapersInstaller:
    def __init__(self, logger, dry_run: bool = False):
        self.dry_run = dry_run

        self.logger = logger

        self.console = get_console()

        self.repo_url = "https://github.com/sbalghari/Wallpapers.git"
        self.clone_dir = Path("/tmp/wallpapers_collection")

    def _clone_repo(self, repo_url: str, clone_dir: Path) -> bool:
        """Clone a git repository into the given directory."""
        try:
            subprocess.run(
                ["git", "clone", repo_url, str(clone_dir)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.logger.info("Cloned repository successfully.")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to clone repository: {e}")
            return False

    def _install_wallpaper_collection(self, spinner: Spinner) -> bool:
        """Clone and install wallpaper collection."""
        if self.clone_dir.exists():
            shutil.rmtree(self.clone_dir)

        sleep(1)  # delay for better UX
        spinner.update_text("Cloning wallpaper repository...")
        if not self._clone_repo(self.repo_url, self.clone_dir):
            return False

        try:
            spinner.update_text("Copying wallpapers...")
            USER_WALLPAPERS_DIR.mkdir(parents=True, exist_ok=True)
            for file in self.clone_dir.iterdir():
                if file.is_file() and file.suffix.lower() in [
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp",
                ]:
                    shutil.copy2(file, USER_WALLPAPERS_DIR)
            self.logger.info("Wallpaper collection copied successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to copy wallpapers: {e}")
            return False

    def install(self) -> bool:
        """Main installer function for wallpapers."""
        self.logger.log_heading("Wallpapers installer started")
        print_header("Installing Wallpapers.")
        print_newline()

        with Spinner("Installing wallpapers...") as spinner:
            try:
                USER_WALLPAPERS_DIR.mkdir(parents=True, exist_ok=True)
                self.logger.info("Ensured wallpapers dir exists.")

                spinner.update_text("Copying default wallpapers...")
                if not self.dry_run:
                    sleep(1)
                    try:
                        shutil.copytree(
                            SBDOTS_WALLPAPERS_DIR,
                            USER_WALLPAPERS_DIR,
                            dirs_exist_ok=True,
                        )
                    except Exception as e:
                        self.logger.error(f"Failed to copy default wallpapers: {e}")
                        return False

                spinner.success("Wallpapers installed successfully.")

            except Exception as e:
                self.logger.error(f"Wallpaper installation failed: {e}")
                spinner.error("Wallpaper installation failed.")
                return False

        sleep(0.5)
        with self.console.screen():
            install_collection = confirm(
                "Do you want to install my wallpapers collection?"
            )

        print_newline()
        if install_collection:
            self.logger.info("User chose to install wallpaper collection.")
            with Spinner("Installing wallpaper collection...") as spinner:
                if self.dry_run:
                    sleep(1)
                if not self.dry_run:
                    if not self._install_wallpaper_collection(spinner):
                        spinner.error("Failed to install wallpaper collection.")
                        return False
                spinner.success("Successfully installed wallpaper collection.")
        else:
            self.logger.info("User chose not to install wallpaper collection.")

        return True
