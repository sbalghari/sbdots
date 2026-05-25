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

from .components import ComponentsManager
from ._validators import is_already_installed
from .postinstall import PostInstallHooks


class SBDotsInitializer:
    def __init__(
        self,
        logger: logging.Logger,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> None:
        self.dry_run = dry_run
        self.verbose = verbose
        self.failed_steps = []

        # Setup logger
        self.logger = logger

        # console
        self.console = get_console()

        # Initialize sub-managers
        self.validator = is_already_installed
        self.components = ComponentsManager(
            self.logger, dry_run=self.dry_run, verbose=self.verbose
        )
        self.post_install_hooks = PostInstallHooks(
            self.logger, dry_run=self.dry_run, verbose=self.verbose
        )

    def _title(self) -> None:
        print_ascii_art("SBDots Installer")
        print_subtext("Welcome to SBDots initializer!")
        print_subtext(
            "This setup will copy sbdots files to the respective user dirs and apply settings."
        )
        print_newline()

        if self.dry_run:
            print_subtext("Dry-run mode enabled. No changes will be made.")
        if self.verbose:
            print_subtext("Verbose mode enabled. Might be noisy.")
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
                "SBDots initialization completed successfully!",
                details="Please restart your PC once before using...",
            )
            sleep(0.5)

            sys.exit(0)
        else:
            if self.failed_steps:
                fails: str = ""
                for component in self.failed_steps:
                    fails += f"  - {component} \n"
                print_error(
                    "The following components failed to initialize: ",
                    details="\n" + fails,
                )
                print_newline()

            print_error(
                "SBDots initialization failed. Please check the logs for details"
            )
            sys.exit(1)

    def _postinstall(self) -> bool:
        self.logger.info(f"{'=' * 50}\nPost install\n{'=' * 50}")
        print_header("Post install hooks")

        with Spinner("Running post install hooks...", verbose=self.verbose) as spinner:
            result = self.post_install_hooks.run_hooks(spinner)
            self.failed_steps.extend(self.post_install_hooks.failed_steps)
            return result

    def install(self) -> None:
        self.logger.info("SBDots Installer initialized")

        if self.validator(self.logger) and not self.dry_run:
            print_warning(
                "SBDots is already initialized for the current user!",
                details="If you want to repair, please remove existing files first.",
            )

        if not confirm(
            message="Do you want to start the initialization?", default_yes=True
        ):
            print_warning(
                "SBDots initialization cancelled!",
                details="If you want to initialize SBDots, please run 'sbdots init'.",
            )
            sleep(1)
            sys.exit(1)

        self.logger.info("Starting SBDots initialization process...")

        if not self.components.install(self.sep_console_screen):
            self.sep_console_screen(lambda: self._exit(success=False))
        self.failed_steps.extend(self.components.failed_steps)

        if not self.sep_console_screen(lambda: self._postinstall()):
            self.sep_console_screen(lambda: self._exit(success=False))

        # Success exit
        self.sep_console_screen(lambda: self._exit(success=True))
