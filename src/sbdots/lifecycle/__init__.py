from time import sleep
from typing import Callable
import logging
import sys

from sbdots.library.cli_utils import (
    Spinner,
    print_ascii_art,
    print_subtext,
    print_success,
    print_warning,
    print_error,
    print_header,
    clear_console,
    confirm,
    get_console,
    print_newline,
)

from .components import (
    DotfilesInstaller,
    WallpapersInstaller,
    OptPackagesInstaller,
    AutoPowerSaverInstaller,
)

from sbdots.constants import (
    WELCOME_MESSAGE,
    SETUP_DESCRIPTION,
    DRY_RUN_MESSAGE,
    VERBOSE_MESSAGE,
    ALREADY_INSTALLED_MESSAGE,
    ALREADY_INSTALLED_DETAILS,
    INSTALLATION_CANCELLED_MESSAGE,
    INSTALLATION_CANCELLED_DETAILS,
    INSTALLATION_SUCCESS_MESSAGE,
    INSTALLATION_SUCCESS_DETAILS,
    INSTALLATION_FAILED_MESSAGE,
    INSTALLATION_FAILED_COMPONENTS_HEADER,
    CONFIRMATION_MESSAGE,
    FINALIZATION_HEADER,
)
from ._validators import is_already_installed
from ._finalization import FinalizationManager


class SBDotsInstaller:
    def __init__(
        self,
        logger: logging.Logger,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> None:
        self.dry_run = dry_run
        self.verbose = verbose
        self.failed_components: list[str] = []

        # Setup logger
        self.logger = logger

        # console
        self.console = get_console()

        # Initialize sub-managers
        self.validator = is_already_installed
        self.finalization_manager = FinalizationManager(
            self.logger, dry_run=self.dry_run, verbose=self.verbose
        )

        self.logger.info("SBDots Installer initialized")

    def _title(self) -> None:
        print_ascii_art("SBDots Installer")
        print_subtext(WELCOME_MESSAGE)
        print_subtext(SETUP_DESCRIPTION)
        print_newline()

        if self.dry_run:
            print_subtext(DRY_RUN_MESSAGE)
        if self.verbose:
            print_subtext(VERBOSE_MESSAGE)
        print_newline()

    def _clear(self) -> None:
        clear_console()

    def sep_console_screen(self, function: Callable):
        if not self.verbose:
            with self.console.screen():
                self._clear()
                self._title()
                result: bool = function()

            return result

        else:
            return function()

    def _exit(self, success: bool = False) -> None:
        print_newline(2)

        if success:
            print_success(
                INSTALLATION_SUCCESS_MESSAGE,
                details=INSTALLATION_SUCCESS_DETAILS,
            )
            sleep(0.5)

            sys.exit(0)
        else:
            if self.failed_components:
                fails: str = ""
                for component in self.failed_components:
                    fails += f"  - {component} \n"
                print_error(
                    INSTALLATION_FAILED_COMPONENTS_HEADER, details="\n" + fails
                )
                print_newline()

            print_error(INSTALLATION_FAILED_MESSAGE)
            sys.exit(1)

    def install_components(self) -> bool:
        self.logger.info("Starting installation of main components...")

        components: dict[str, Callable[[], bool]] = {
            "Dotfiles": lambda: DotfilesInstaller(
                dry_run=self.dry_run, logger=self.logger, verbose=self.verbose
            ).install(),
            "Recommended Packages": lambda: OptPackagesInstaller(
                dry_run=self.dry_run, logger=self.logger, verbose=self.verbose
            ).install(),
            "Wallpapers": lambda: WallpapersInstaller(
                dry_run=self.dry_run, logger=self.logger, verbose=self.verbose
            ).install(),
        }

        all_success = True

        for component_name, install_func in components.items():
            self.logger.info(f"Installing {component_name}...")

            try:
                if self.sep_console_screen(lambda: install_func()):
                    self.logger.info(
                        f"{component_name} installed successfully."
                    )
                else:
                    self.logger.error(f"{component_name} installation failed.")
                    self.failed_components.append(component_name)
                    all_success = False
            except Exception as e:
                self.logger.error(
                    f"Unexpected error installing {component_name}: {e}"
                )
                self.failed_components.append(component_name)
                all_success = False

        return all_success

    def install_optional_components(self) -> bool:
        """Install optional components that are not critical for basic functionality."""
        self.logger.info("Installing optional components...")

        optional_success = True

        # Install auto power saver (non-critical), only for laptops
        try:
            if not self.sep_console_screen(
                lambda: AutoPowerSaverInstaller().install(
                    logger=self.logger,
                    dry_run=self.dry_run,
                    verbose=self.verbose,
                )
            ):
                self.logger.warning(
                    "Couldn't install auto power saver, continuing..."
                )
                self.failed_components.append("Auto power saver")
        except Exception as e:
            self.logger.error(f"Error installing auto power saver: {e}")
            optional_success = False

        return optional_success

    def finalize_installation(self) -> bool:
        """
        Perform final installation steps.

        Returns:
            bool: True if finalization completed (even with minor errors), False if critical error
        """
        self.logger.info("Finalizing installation")
        print_header(FINALIZATION_HEADER)

        with Spinner(
            "Finalizing SBDots initialization...", verbose=self.verbose
        ) as spinner:
            result = self.finalization_manager.finalize(spinner)
            self.failed_components.extend(
                self.finalization_manager.failed_steps
            )
            return result

    def install(self) -> None:
        """Main installation method."""

        if self.validator(self.logger) and not self.dry_run:
            print_warning(
                ALREADY_INSTALLED_MESSAGE,
                details=ALREADY_INSTALLED_DETAILS,
            )

        if not confirm(message=CONFIRMATION_MESSAGE, default_yes=True):
            print_warning(
                INSTALLATION_CANCELLED_MESSAGE,
                details=INSTALLATION_CANCELLED_DETAILS,
            )
            sleep(1)
            sys.exit(1)

        self.logger.info("Starting SBDots installation process...")

        # Install main components
        self.logger.info("Installing main components...")
        if not self.install_components():
            self.logger.error("Main components installation failed.")
            self.sep_console_screen(lambda: self._exit(success=False))

        # Install optional components
        self.logger.info("Installing optional components...")
        if not self.install_optional_components():
            self.logger.warning(
                "Some optional components failed, but continuing..."
            )

        # Finalize installation
        self.logger.info("Finalizing installation...")
        if not self.sep_console_screen(lambda: self.finalize_installation()):
            self.logger.error("Finalization phase failed.")
            self.sep_console_screen(lambda: self._exit(success=False))

        # Success exit
        self.sep_console_screen(lambda: self._exit(success=True))
