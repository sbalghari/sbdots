from logging import Logger
import subprocess
from pathlib import Path

from sbdots.library.fs_ops import copy, remove
from sbdots.library.cli_utils import (
    print_header,
    Spinner,
    confirm,
    get_console,
    print_newline,
)
from sbdots.constants import (
    SBDOTS_WALLPAPERS_DIR,
    SBDOTS_CONFIG_DIR,
    USER_WALLPAPERS_DIR,
    SBDOTS_DATA_DIR,
)


class WallpapersInstaller:
    def __init__(self, logger: Logger, dry_run: bool, verbose: bool):
        self.logger = logger
        self.verbose = verbose
        self.dry_run = dry_run

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
            remove(self.clone_dir, logger=self.logger)

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
                    if not copy(file, USER_WALLPAPERS_DIR, logger=self.logger):
                        spinner.error("Failed to copy wallpapers, check logs")
                        return False

        except Exception as e:
            self.logger.exception(
                "Unexpected error while copying wallpapers.", exc_info=e
            )
            return False

        self.logger.info("Wallpaper collection copied successfully.")
        return True

    def install(self) -> bool:
        """Main installer function for wallpapers."""
        self.logger.info("Wallpapers installer started")
        print_header("Installing Wallpapers.")
        print_newline()

        with Spinner("Installing wallpapers...", verbose=self.verbose) as spinner:
            try:
                USER_WALLPAPERS_DIR.mkdir(parents=True, exist_ok=True)
                self.logger.info("Ensured wallpapers dir exists.")

                spinner.update_text("Copying default wallpapers...")
                if not self.dry_run:
                    try:
                        avatar = SBDOTS_DATA_DIR / "avatar.png"
                        avatar_dst = SBDOTS_CONFIG_DIR / '.avatar'
                        copy_success = all(
                            [
                                copy(
                                    SBDOTS_WALLPAPERS_DIR,
                                    USER_WALLPAPERS_DIR,
                                    logger=self.logger,
                                ),
                                copy(avatar, avatar_dst, logger=self.logger),
                            ]
                        )
                        if not copy_success:
                            spinner.error(
                                "Failed to copy default wallpapers, check logs."
                            )
                            return False
                    except Exception as e:
                        self.logger.error(f"Failed to copy default wallpapers: {e}")
                        return False

                spinner.success("Wallpapers installed successfully.")

            except Exception as e:
                self.logger.exception("Wallpaper installation failed", exc_info=e)
                return False

        install_collection = confirm(
            message="Do you want to install my wallpapers collection?",
            default_yes=False,
        )

        print_newline()
        if install_collection:
            self.logger.info("User chose to install wallpaper collection.")
            with Spinner(
                "Installing wallpaper collection...", verbose=self.verbose
            ) as spinner:
                if not self.dry_run:
                    if not self._install_wallpaper_collection(spinner):
                        spinner.error("Failed to install wallpaper collection.")
                        return False
                spinner.success("Successfully installed wallpaper collection.")
        else:
            self.logger.info("User chose not to install wallpaper collection.")

        return True
