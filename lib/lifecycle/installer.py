from time import sleep
from typing import Dict, Callable, List
import sys

from utils.logger import Logger
from utils.paths import SBDOTS_LOG_DIR
from library.run_cmd import run_command
from library.tui import (
    Spinner,
    print_asci_title,
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
    PackagesInstaller,
    AutoPowerSaverInstaller,
)

from .postinstall import (
    apply_gtk_theme,
    apply_wallpaper,
    reload_hyprland,
    start_actionsd,
)

from utils.paths import (
    USER_DOTFILES_DIR,
    USER_WALLPAPERS_DIR,
    SBDOTS_CONFIG_DIR,
)


class SBDotsInstaller:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.failed_components: List[str] = []

        # Setup logger
        self.logfile = SBDOTS_LOG_DIR / "installer.log"
        self.logger = Logger(log_file=self.logfile)

        # console
        self.console = get_console()

        # Ensure log file is empty at start
        try:
            with open(self.logfile, "w") as f:
                f.write("")
        except IOError as e:
            print_error(f"Could not clear log file: {e}")

        self.logger.log_heading("SBDots Installer initialized")

    def _is_already_installed(self) -> bool:
        """
        Check whether SBDots is already installed by verifying the existence
        of key components and directories.
        """
        self.logger.log_heading("Checking for existing SBDots installation")

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
        print_asci_title("SBDots")
        print_subtext("Welcome to SBDots installer!")
        print_subtext("A clean, full-featured, and aesthetic Hyprland Setup.")
        print_subtext("An open-source project by Saifullah Balghari")
        print_newline()

        if self.dry_run:
            print_subtext("Dry run mode enabled. No changes will be made.")
            print_newline()

    def _clear(self) -> None:
        clear_console()

    def sep_console_screen(self, function: Callable) -> bool:
        with self.console.screen():
            self._clear()
            self._title()
            result: bool = function()

        return result

    def _exit(self, success: bool = False) -> None:
        print_newline(2)

        if success:
            print_success("SBDots installation completed successfully!")
            print_subtext("Please restart your PC once before using...")
            sleep(1)

            reboot: bool = False
            with self.console.screen():
                reboot = confirm(prompt="Do you want to reboot now?", default_yes=False)

            if reboot:
                print_warning("Rebooting...")
                sleep(1)
                try:
                    run_command(["reboot"])
                except Exception as e:
                    print_error(f"Failed to reboot automatically: {e}")
                    print_subtext("Please reboot manually.")
            sys.exit(0)
        else:
            if self.failed_components:
                print_error("The following components failed to install:")
                for component in self.failed_components:
                    print_subtext(f"  - {component}")
                print_newline()

            print_error(
                f"SBDots installation failed. Please check the logs for details: {self.logfile}"
            )
            sys.exit(1)

    def install_components(self) -> bool:
        self.logger.info("Starting installation of main components...")

        components: Dict[str, Callable[[], bool]] = {
            "Dotfiles": lambda: DotfilesInstaller(
                dry_run=self.dry_run, logger=self.logger
            ).install(),
            "Packages": lambda: PackagesInstaller(
                dry_run=self.dry_run, logger=self.logger
            ).install(),
            "Wallpapers": lambda: WallpapersInstaller(
                dry_run=self.dry_run, logger=self.logger
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

        # Install optional applications (non-critical)
        try:
            if not self.sep_console_screen(
                lambda: PackagesInstaller(
                    dry_run=self.dry_run, logger=self.logger
                ).install_optional_applications()
            ):
                self.logger.warning(
                    "Couldn't install some optional applications, continuing..."
                )
                self.failed_components.append("Some optional applications")
        except Exception as e:
            self.logger.error(f"Error installing optional applications: {e}")
            optional_success = False

        # Install auto power saver (non-critical), only for laptops
        try:
            if not self.sep_console_screen(
                lambda: AutoPowerSaverInstaller().install(
                    logger=self.logger, dry_run=self.dry_run
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
        self.logger.log_heading("Finalizing installation")
        print_header("Finalizing installation:")

        with Spinner("Finalizing SBDots installation...") as spinner:
            finalization_steps = [
                (
                    "Starting SBDots Actions...",
                    lambda: start_actionsd(logger=self.logger, dry_run=self.dry_run),
                    True,
                ),  # critical
                (
                    "Reloading Hyprland...",
                    lambda: reload_hyprland(dry_run=self.dry_run),
                    True,
                ),  # Critical
                (
                    "Installing GTK Catppuccin theme...",
                    lambda: apply_gtk_theme(
                        spinner=spinner, logger=self.logger, dry_run=self.dry_run
                    ),
                    False,
                ),  # Non-critical
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

                sleep(1)  # Small delay b/w steps for better UX

            if all_success:
                spinner.success("Finalization completed successfully.")
            else:
                spinner.error("Finalization failed.")

        return all_success

    def install(self) -> None:
        """Main installation method."""

        if self._is_already_installed() and not self.dry_run:
            print_warning("SBDots is already installed.")
            print_subtext(
                "If you want to reinstall or repair, please remove existing files first."
            )
            print_newline()
            sleep(2)
            sys.exit(0)

        if not self.sep_console_screen(
            lambda: confirm(
                prompt="Do you want to start the installation?", default_yes=True
            )
        ):
            print_warning("SBDots installation cancelled!")
            print_subtext(
                "If you want to install SBDots, please run 'sbdots --install'."
            )
            print_newline()
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
