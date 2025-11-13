from time import sleep
from typing import Dict, List
from pathlib import Path
import subprocess
import json

from library import is_installed, install_package, remove_package, SudoKeepAlive
from utils.paths import (
    HYPRLAND_PKGS,
    CORE_PKGS,
    FONTS,
    APPLICATIONS,
    THEMING_PKGS,
    OPTIONAL_PKGS,
)
from library.tui import (
    Spinner,
    choose,
    print_header,
    print_newline,
    print_success,
    print_info,
    print_error,
    get_console,
)


class PackagesInstaller:
    def __init__(self, logger, dry_run: bool = False):
        self.dry_run = dry_run
        self.logger = logger
        self.console = get_console()

        # Load package lists
        self.core: List[str] = self._get_packages_list(CORE_PKGS)
        self.hyprland: List[str] = self._get_packages_list(HYPRLAND_PKGS)
        self.applications: List[str] = self._get_packages_list(APPLICATIONS)
        self.fonts: List[str] = self._get_packages_list(FONTS)
        self.theming: List[str] = self._get_packages_list(THEMING_PKGS)
        self.optional: List[str] = self._get_packages_list(OPTIONAL_PKGS)

    def install(self) -> bool:
        self.logger.log_heading("Packages installer started")
        print_header("Installing packages.")

        groups: Dict[str, List[str]] = {
            "Core packages": self.core,
            "Hyprland packages": self.hyprland,
            "Theming packages": self.theming,
            "Fonts": self.fonts,
            "Applications": self.applications,
        }

        print_info(
            "Installing packages(dependencies), This might take a while. please be patient."
        )
        print_newline()
        self.logger.info("Installing packages(dependencies)...")

        # Remove conflicts if they exist
        conflicting_pkgs: List[str] = ["wofi", "dunst"]
        conflicts: list[str] = [pkg for pkg in conflicting_pkgs if is_installed(pkg)]

        if conflicts and not self.dry_run:
            self.logger.info(f"Found conflicts: {conflicts}, removing them...")
            print_info("Removing conflicting packages...")

            failed_removals: list[str] = []
            for pkg in conflicts:
                with Spinner(f"Removing {pkg}") as spinner:
                    if remove_package(logger=self.logger, package=pkg):
                        spinner.success(f"Removed {pkg}")
                    else:
                        spinner.error(f"Failed to remove {pkg}")
                        failed_removals.append(pkg)

            if failed_removals:
                print_error(f"Failed to remove conflicting packages: {failed_removals}")
                print()
                print_error(
                    "Installation will continue but SBDots may not work properly."
                )
                print_error("Please remove them manually!")
            else:
                print_success("All conflicting packages removed successfully!")

            print_newline()

        for title, packages_list in groups.items():
            with Spinner(f"Installing {title}") as spinner:
                sleep(1)

                # Filter out already installed packages
                packages_list = [pkg for pkg in packages_list if not is_installed(pkg)]

                if not packages_list:
                    self.logger.info(f"All {title} are already installed, Skipping.")
                    spinner.success(f"{title} are already installed, skipping...")
                    continue

                failed_pkgs: List = []
                for pkg in packages_list:
                    spinner.update_text(f"Installing package: {pkg}")

                    if self.dry_run:
                        sleep(0.1)
                        continue

                    if not install_package(logger=self.logger, package=pkg):
                        spinner.error(f"Couldn't install package: {pkg}")
                        failed_pkgs.append(pkg)

                if failed_pkgs:
                    self.logger.error(f"Error installing packages: {failed_pkgs}")
                    return False
                spinner.success(f"Successfully installed {title}.")

        return True

    def install_optional_applications(self) -> bool:
        self.logger.log_heading("Optional packages installer started")
        print_header("Installing optional applications.")
        print_newline()

        sleep(1)
        with self.console.screen():
            chosen: list[str] | str | None = choose(
                *self.optional, prompt="Choose apps to install.", no_limit=True
            )

        if not chosen:
            self.logger.info("No optional packages selected, skipping...")
            print_info("No optional packages selected, skipping...")
            return True

        self.logger.info(f"Chosen packages: {', '.join(chosen)}")

        if self.dry_run:
            for i in chosen:
                with Spinner(f"Installing {i}") as spinner:
                    sleep(0.5)
                    spinner.success(f"{i} successfully installed.")
                    sleep(0.5)

            return True

        # Filter out already installed packages
        chosen = [pkg for pkg in chosen if not is_installed(pkg)]

        if not chosen:
            print_success(
                "All chosen optional packages are already installed, skipping..."
            )
            self.logger.info(
                "All chosen optional packages are already installed, skipping..."
            )

            return True

        failed_pkgs: List[str] = []

        with SudoKeepAlive(max_duration=1800):  # 30 minutes max duration
            for pkg in chosen:
                with Spinner(f"Installing {pkg}") as spinner:
                    try:
                        # Attempt to install the package
                        if install_package(package=pkg, logger=self.logger):
                            self.logger.info(f"Package: {pkg} installed.")
                            spinner.success(f"Installed {pkg}")
                        else:
                            self.logger.error(f"Package: {pkg} failed to installed.")
                            spinner.error(f"Failed to install {pkg}")
                            failed_pkgs.append(pkg)

                    except subprocess.TimeoutExpired:
                        self.logger.error(
                            f"Package {pkg} failed to install due to Timeout."
                        )
                        spinner.error(f"Timeout while installing {pkg}")
                        failed_pkgs.append(pkg)

                    except subprocess.CalledProcessError as e:
                        self.logger.error(
                            f"Package {pkg} failed to install.", exc_info=e
                        )
                        spinner.error(f"Error installing {pkg}: {str(e)}")
                        failed_pkgs.append(pkg)

                    except Exception as e:
                        spinner.error(
                            f"Unexpected error installing {pkg}: {str(e)}", log=True
                        )
                        failed_pkgs.append(pkg)

        if failed_pkgs:
            print_error(
                f"Failed to install {len(failed_pkgs)} package(s): {', '.join(failed_pkgs)}"
            )
            self.logger.error(f"Error installing packages: {failed_pkgs}")

            return False
        else:
            print_success("All optional packages installed successfully!")
            self.logger.info("All optional packages installed successfully!")

        return True

    def _get_packages_list(self, filepath: Path) -> List[str]:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError(f"Expected a list in {filepath}, got {type(data)}")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            if isinstance(e, FileNotFoundError):
                self.logger.error(f"Package list {filepath} not found.")
            else:
                self.logger.error(f"Package list {filepath} is not valid JSON.")
            raise
