import subprocess

from sbdots.library.pkg_utils import is_installed, install_package
from sbdots.library.sudo_keep_alive import SudoKeepAlive
from sbdots.library.cli_utils import (
    Spinner,
    chose,
    print_header,
    print_newline,
    print_success,
    print_info,
    print_error,
    get_console,
)


class OptPackagesInstaller:
    def __init__(self, logger, dry_run, verbose):
        self.logger = logger
        self.verbose = verbose
        self.dry_run = dry_run
        self.console = get_console()

        # TODO: add discribtions
        self.optional_pkgs = [
            "visual-studio-code-bin",
            "vlc",
            "smile",
            "sddm",
            "obs-studio",
            "mission-center",
            "loupe",
            "libreoffice-fresh",
            "gnome-text-editor",
            "ark",
        ]

    def install(self) -> bool:
        self.logger.info("Optional packages installer started")
        print_header("Installing optional applications.")
        print_newline()

        chosen: list[str] | str | None = chose(
            choices=self.optional_pkgs, message="Choose apps to install."
        )

        if not chosen:
            print_info("No optional packages selected, skipping...")
            return True

        self.logger.info(f"Chosen packages: {', '.join(chosen)}")

        if self.dry_run:
            for i in chosen:
                with Spinner(f"Installing {i}", verbose=self.verbose) as spinner:
                    spinner.success(f"{i} successfully installed.")

            return True

        # Filter out already installed packages
        chosen = [pkg for pkg in chosen if not is_installed(pkg)]

        if not chosen:
            print_success(
                "All chosen optional packages are already installed, skipping..."
            )

            return True

        failed_pkgs: list[str] = []

        with SudoKeepAlive(max_duration=1800):  # 30 minutes max duration
            for pkg in chosen:
                with Spinner(f"Installing {pkg}", verbose=self.verbose) as spinner:
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
                        spinner.error(f"Unexpected error installing {pkg}: {str(e)}")
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
