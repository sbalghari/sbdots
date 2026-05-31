from sbdots.library.notify import notify_send
from sbdots.library.commands import check_output, run_sudo_cmd
from sbdots.library.cli_utils import (
    print_error,
    print_info,
    print_success,
    print_warning,
    print_subtext,
    print_newline,
    confirm,
    Spinner,
    print_ascii_art,
)

from typing import Optional
from logging import Logger


class InstallUpdates:
    def __init__(self, logger: Logger, verbose: bool = False) -> None:
        self.aur_helper = self._get_aur_helper()
        self.logger = logger
        self.verbose = verbose

    def _get_aur_helper(self) -> str | None:
        """Detect available AUR helper (yay or paru)."""
        if check_output("command -v yay"):
            return "yay"
        elif check_output("command -v paru"):
            return "paru"
        else:
            return None

    def _run_command(self, cmd, spinner: Optional[Spinner] = None) -> bool:
        rc = run_sudo_cmd(
            command=cmd,
            spinner=spinner,
            logger=self.logger,
            verbose=self.verbose,
        )

        if not rc and rc != 0:
            self.logger.error("error")
            return False

        return True

    def main(self) -> None:
        # Header
        print_ascii_art("System Updates")
        print_subtext("It is recommended to install updates 3-4 times a week.")
        print_newline(2)

        # Check for AUR helper
        if not self.aur_helper:
            print_error("ERROR - No AUR helper found (yay or paru).")
            return

        print_info(f"Using AUR helper: {self.aur_helper}")
        print_newline()

        # Confirm update start
        if not confirm("Do you want to start the full system update now?"):
            print_warning("Update canceled.")
            return

        print_info("UPDATE STARTED")
        print_newline()

        with Spinner("Installing updates...") as spinner:
            # System updates
            if not self._run_command(
                cmd="sudo pacman -Syu --noconfirm", spinner=spinner
            ):
                print_error("System update installation has failed")
                return

            # AUR updates
            if not self._run_command(
                cmd=f"{self.aur_helper} -Syu --noconfirm", spinner=spinner
            ):
                print_error("Aur update installation has failed")
                return

        # Cleanup orphaned packages
        print_newline()
        if confirm("Do you want to clean up orphaned packages?"):
            # Check for orphans
            import subprocess

            result = subprocess.run(
                "pacman -Qdtq", shell=True, capture_output=True, text=True
            )
            orphans = result.stdout.strip()

            if orphans:
                print_warning("Orphaned packages found:")
                print_subtext(orphans)

                # Remove orphans
                cmd = f"pacman -Rns {orphans.replace(chr(10), ' ')} --noconfirm"
                self._run_command(cmd)
            else:
                print_success("No orphaned packages found")
        else:
            print_warning("Skipping orphan cleanup")

        # Clean package cache
        print_newline()
        if confirm("Do you want to clean package cache? (Free disk space)"):
            self._run_command("pacman -Sc --noconfirm")

            # Clean AUR cache based on helper
            if self.aur_helper == "yay":
                self._run_command("yay -Sc --noconfirm")
            elif self.aur_helper == "paru":
                self._run_command("paru -Sc --noconfirm")

        # Final summary
        print_newline()
        print_success("UPDATE COMPLETE")

        # Notify
        notify_send(
            "System Update",
            "All updates completed successfully!",
        )

        # Reboot check
        print_newline()
        if confirm("Updates complete. Some updates may require a reboot. Reboot now?"):
            self._run_command("reboot")

        print_newline()
        print_success("All updates completed successfully!")
        print_newline()
        print_info("Press [ENTER] to close.")
        input()
