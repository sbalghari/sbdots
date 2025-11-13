from pathlib import Path
from typing import List, Tuple
from time import sleep

from library import remove, create_symlink, path_lexists, copy
from utils.paths import USER_CONFIGS_DIR, USER_DOTFILES_DIR, SBDOTS_DOTFILES_DIR
from library.tui import print_header, Spinner


class DotfilesInstaller:
    def __init__(self, logger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run
        self.dotfiles_components = [
            "hypr",
            "waybar",
            "rofi",
            "fish",
            "kitty",
            "neofetch",
            "fastfetch",
            "cava",
            "waypaper",
            "swaync",
            "btop",
            "systemd",
            "wlogout",
            "atuin",
            "starship.toml",
        ]

        self.source_dotfiles_components_paths = [
            SBDOTS_DOTFILES_DIR / i for i in self.dotfiles_components
        ]
        self.target_dotfiles_components_paths = [
            USER_DOTFILES_DIR / i for i in self.dotfiles_components
        ]

    def install(self):
        self.logger.log_heading("Dotfiles installer started")
        print_header("Installing dotfiles.")

        with Spinner("Installing dotfiles...") as spinner:
            sleep(1)  # delay for better UX

            # Step 1: Check if source files exists
            if not self._validate_sources(spinner):
                return False
            # Step 2: Copy Dotfiles
            if not self._copy_dotfiles(spinner):
                return False
            # Step 3: Check if Dotfiles copied or not
            if not self._verify_copy(spinner):
                return False
            # Step 4: Remove existing old configs
            if not self._remove_existing_configs(spinner):
                return False
            # Step 5: Link the new Dotfiles
            if not self._create_links(spinner):
                return False

            sleep(1)
            spinner.success("Dotfiles installed successfully!")

        return True

    def _validate_sources(self, spinner) -> bool:
        self.logger.info("Validating source dotfiles components.")
        spinner.update_text("Validating source dotfiles components...")
        if self.dry_run:
            sleep(1)
            return True
        for i in self.source_dotfiles_components_paths:
            if not path_lexists(i):
                self.logger.error(f"Missing source: {i}.")
                spinner.error(f"Missing source: {i}, exiting...")
                return False
        return True

    def _copy_dotfiles(self, spinner) -> bool:
        self.logger.info(f"Copying dotfiles to {USER_DOTFILES_DIR}")
        spinner.update_text("Copying dotfiles...")

        if self.dry_run:
            sleep(2)
            return True

        self.logger.info("Creating dotfiles dir...")
        if USER_DOTFILES_DIR.exists():
            self.logger.info("Dotfiles dir already exists, removing it...")
            remove(logger=self.logger, filepath=USER_DOTFILES_DIR)

        self.logger.info("Copying...")
        try:
            copy(logger=self.logger, src=SBDOTS_DOTFILES_DIR, dest=USER_DOTFILES_DIR)
        except Exception as e:
            self.logger.error(f"Failed to copy dotfiles: {e}")
            spinner.error("Failed to copy dotfiles.")
            return False
        return True

    def _verify_copy(self, spinner) -> bool:
        self.logger.info("Checking if copied successfully or not.")

        if self.dry_run:
            return True

        missing: list = []
        for i in self.target_dotfiles_components_paths:
            if not path_lexists(i):
                self.logger.error(f"Copied dotfile component {i} is missing.")
                missing.append(i)

        if missing:
            spinner.error("Some dotfile components are missing, exiting...")
            return False

        return True

    def _remove_existing_configs(self, spinner) -> bool:
        self.logger.info("Removing existing configs.")
        spinner.update_text("Removing existing configs...")

        if self.dry_run:
            sleep(1)
            return True

        for i in self.dotfiles_components:
            file: Path = USER_CONFIGS_DIR / i
            if not remove(logger=self.logger, filepath=file):
                spinner.error(f"Failed to remove existing config: {file}.")
                return False
        return True

    def _create_links(self, spinner) -> bool:
        self.logger.info("Creating system links.")
        spinner.update_text("Linking new dotfiles...")

        if self.dry_run:
            sleep(1)
            return True

        failed_links: List[Tuple[Path, Path]] = []
        for component in self.dotfiles_components:
            source: Path = USER_DOTFILES_DIR / component
            target: Path = USER_CONFIGS_DIR / component
            if not create_symlink(logger=self.logger, source=source, target=target):
                self.logger.error(f"Failed to link {source} to {target}.")
                failed_links.append((source, target))

        if failed_links:
            spinner.error("Failed to create some links, exiting...")
            return False

        return True
