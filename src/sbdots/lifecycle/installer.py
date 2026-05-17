from time import sleep
from typing import Dict, Callable, List
from pathlib import Path
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

from .postinstall import (
    apply_gtk_theme,
    apply_wallpaper,
    reload_hyprland,
    start_services,
)

HOME = Path.home()
USER_CONFIGS_DIR = HOME / ".config"
USER_DOTFILES_DIR = HOME / "Dotfiles"
USER_WALLPAPERS_DIR = HOME / "Wallpapers"
SBDOTS_CONFIG_DIR = HOME / ".sbdots"


class SBDotsInstaller:
    def __init__(
        self, logger_name, dry_run: bool = False, verbose: bool = False
    ) -> None:
        self.dry_run = dry_run
        self.verbose = verbose
        self.failed_components: List[str] = []

        # Setup logger
        self.logger = logging.getLogger(logger_name)

        # console
        self.console = get_console()

        self.logger.info("SBDots Installer initialized")

    def _is_already_installed(self) -> bool:
        """
        Check whether SBDots is already installed by verifying the existence
        of key components and directories.
        """
        self.logger.info("Checking for existing SBDots installation")

        # Core existence checks
        checks: Dict[str, bool] = {
            "Dotfiles directory": USER_DOTFILES_DIR.exists(),
            "Wallpapers directory": USER_WALLPAPERS_DIR.exists(),
            "SBDots config directory": SBDOTS_CONFIG_DIR.exists(),
        }

        # Log each check
        for name, exists in checks.items():
            status = "FOUND" if exists else "MISSING"
            self.logger.info(f"{name}: {status}")

        # Check if all user dotfile components exist
        dotfile_components_exist: bool = all(
            (USER_DOTFILES_DIR / component).exists()
            for component in [
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
        )

        self.logger.info(
            "Dotfile components check: "
            + ("ALL PRESENT" if dotfile_components_exist else "INCOMPLETE")
        )

        critical_paths_exist = (
            checks["Dotfiles directory"]
            and checks["Wallpapers directory"]
            and dotfile_components_exist
        )

        if critical_paths_exist:
            self.logger.info("SBDots appears to be already installed.")
            return True

        self.logger.info("No existing installation detected.")
        return False

    def _title(self) -> None:
        print_ascii_art("SBDots Installer")
        print_subtext("Welcome to SBDots installer!")
        print_subtext(
            "This setup will copy sbdots files to the repective user dirs and apply settings."
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
                "SBDots installation completed successfully!",
                details="Please restart your PC once before using...",
            )
            sleep(0.5)

            sys.exit(0)
        else:
            if self.failed_components:
                fails: str = ""
                for component in self.failed_components:
                    fails += f"  - {component} \n"
                print_error(
                    "The following components failed to install:", details="\n" + fails
                )
                print_newline()

            print_error("SBDots installation failed. Please check the logs for details")
            sys.exit(1)

    def install_components(self) -> bool:
        self.logger.info("Starting installation of main components...")

        components: Dict[str, Callable[[], bool]] = {
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
                    self.logger.info(f"{component_name} installed successfully.")
                else:
                    self.logger.error(f"{component_name} installation failed.")
                    self.failed_components.append(component_name)
                    all_success = False
            except Exception as e:
                self.logger.error(f"Unexpected error installing {component_name}: {e}")
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
                    logger=self.logger, dry_run=self.dry_run, verbose=self.verbose
                )
            ):
                self.logger.warning("Couldn't install auto power saver, continuing...")
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
        print_header("Finalizing installation:")

        with Spinner(
            "Finalizing SBDots installation...", verbose=self.verbose
        ) as spinner:
            finalization_steps = [
                (
                    "Starting SBDots Services...",
                    lambda: start_services(logger=self.logger, dry_run=self.dry_run),
                    True,
                ),  # critical
                (
                    "Reloading Hyprland...",
                    lambda: reload_hyprland(dry_run=self.dry_run),
                    False,
                ),  # Non-critical
                (
                    "Installing GTK Catppuccin theme...",
                    lambda: apply_gtk_theme(
                        spinner=spinner, logger=self.logger, dry_run=self.dry_run
                    ),
                    True,
                ),  # Critical
                (
                    "Applying wallpaper...",
                    lambda: apply_wallpaper(logger=self.logger, dry_run=self.dry_run),
                    False,
                ),  # Non-critical
            ]

            all_success = True

            for step_text, step_func, is_critical in finalization_steps:
                spinner.update_text(step_text)

                try:
                    if not step_func():
                        if is_critical:
                            spinner.error(f"{step_text.strip()} failed.")
                            all_success = False
                            break
                        else:
                            spinner.warning(
                                f"{step_text.strip()} completed with warnings."
                            )
                            self.failed_components.append(step_text.strip(" ."))
                    else:
                        self.logger.info(f"{step_text.strip()} completed successfully.")

                except Exception as e:
                    self.logger.error(
                        f"Unexpected error during {step_text.strip()}: {e}"
                    )
                    if is_critical:
                        spinner.error(f"{step_text.strip()} failed unexpectedly.")
                        all_success = False
                        break
                    else:
                        spinner.warning(f"{step_text.strip()} completed with errors.")
                        self.failed_components.append(step_text.strip(" ."))

            if all_success:
                spinner.success("Finalization completed successfully.")
            else:
                spinner.error("Finalization failed.")

        return all_success

    def install(self) -> None:
        """Main installation method."""

        if self._is_already_installed() and not self.dry_run:
            print_warning(
                "SBDots is already installed.",
                details="If you want to reinstall or repair, please remove existing files first.",
            )
            # sys.exit(0)

        if not confirm(
            message="Do you want to start the installation?", default_yes=True
        ):
            print_warning(
                "SBDots installation cancelled!",
                details="If you want to install SBDots, please run 'sbdots init'.",
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
            self.logger.warning("Some optional components failed, but continuing...")

        # Finalize installation
        self.logger.info("Finalizing installation...")
        if not self.sep_console_screen(lambda: self.finalize_installation()):
            self.logger.error("Finalization phase failed.")
            self.sep_console_screen(lambda: self._exit(success=False))

        # Success exit
        self.sep_console_screen(lambda: self._exit(success=True))
