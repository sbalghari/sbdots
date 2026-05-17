from logging import Logger
from pathlib import Path
from time import sleep

from sbdots.library.fs_ops import remove, create_symlink, path_lexists, copy
from sbdots.library.cli_utils import print_header, Spinner
from sbdots.constants import (
    USER_CONFIGS_DIR,
    USER_DOTFILES_DIR,
    SBDOTS_DOTFILES_DIR,
    REQUIRED_DOTFILE_COMPONENTS,
)


class DotfilesInstaller:
    def __init__(self, logger: Logger, dry_run: bool, verbose: bool):
        self.logger = logger
        self.verbose = verbose
        self.dry_run = dry_run
        self.dotfiles_components = REQUIRED_DOTFILE_COMPONENTS

        self.source_dotfiles_components_paths = [
            SBDOTS_DOTFILES_DIR / i for i in self.dotfiles_components
        ]
        self.target_dotfiles_components_paths = [
            USER_DOTFILES_DIR / i for i in self.dotfiles_components
        ]

    def install(self):
        self.logger.info("Dotfiles installer started")
        print_header("Installing dotfiles.")

        with Spinner(
            "Installing dotfiles...", verbose=self.verbose
        ) as spinner:
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
            if not copy(
                SBDOTS_DOTFILES_DIR,
                USER_DOTFILES_DIR,
                logger=self.logger,
            ):
                spinner.error("Failed to copy dotfiles, check logs")
                return False
        except Exception as e:
            self.logger.exception(
                "Unexpected error while copying dotfiles.", exc_info=e
            )
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

        failed_links: list[tuple[Path, Path]] = []
        for component in self.dotfiles_components:
            source: Path = USER_DOTFILES_DIR / component
            target: Path = USER_CONFIGS_DIR / component
            if not create_symlink(source, target, logger=self.logger):
                self.logger.error(f"Failed to link {source} to {target}.")
                failed_links.append((source, target))

        if failed_links:
            spinner.error("Failed to create some links, exiting...")
            return False

        return True
