from pathlib import Path
from time import sleep

from utils.paths import SBDOTS_UDEV_RULES_DIR
from library import path_lexists, SudoKeepAlive, is_laptop, is_vm, run_command
from library.tui import print_header, Spinner


class AutoPowerSaverInstaller:
    """
    Creates a udev rule to automatically toggle battery saver when a laptop is plugged in or unplugged.
    Additionally, it adjusts screen brightness: 50% when unplugged, 100% when plugged in.
    """

    @staticmethod
    def is_installed() -> bool:
        """Check if auto power saver udev rule is already installed"""
        rule_file = Path("/etc/udev/rules.d/99-power-state.rules")
        return rule_file.exists()

    @staticmethod
    def install(logger, dry_run: bool = False) -> bool:
        logger.log_heading("Setting auto power saver.")

        logger.debug("Checking for VM...")
        if is_vm():
            logger.warning("Running on VM, skipping auto power saver installation...")
            return True

        logger.debug("Checking for Laptop...")
        if not is_laptop(logger=logger):
            logger.warning(
                "Host system is not a laptop, skip setting auto power saver..."
            )
            return True

        print_header("Setting auto power saver.")

        if dry_run:
            with Spinner("Installing auto power saver...") as spinner:
                sleep(1)
                spinner.success("Auto power saver installed successfully.")

            return True

        with SudoKeepAlive(max_duration=60) as sudo:
            if not sudo.is_running:
                logger.error("Failed to get sudo permissions, exiting...")
                return False

            with Spinner("Installing auto power saver...") as spinner:
                sleep(1)  # delay for better UX

                spinner.update_text("Copying udev rule file...")

                src_rule_file = SBDOTS_UDEV_RULES_DIR / "99-power-state.rules"

                # Check if source rule file exists
                if not path_lexists(src_rule_file):
                    logger.error(f"Src rule-file:{src_rule_file} does not exist.")
                    return False

                src = src_rule_file
                dest = Path("/etc/udev/rules.d")

                # Create dest if does not exists
                mkdir_cmd = ["sudo", "mkdir", "-p", dest]
                if not path_lexists(dest):
                    logger.debug(
                        f"Destination dir: {dest} doesn't exists, creating it."
                    )
                    result = run_command(mkdir_cmd)
                    if result.returncode != 0:
                        logger.error(
                            f"Unable to create dir: {dest}, error: {result.stdout} - {result.stderr}"
                        )
                        return False
                    logger.info(f"Destination dir: {dest} created.")

                # Copy
                cp_cmd = ["sudo", "cp", "-f", src, dest]
                result = run_command(cp_cmd)
                if result.returncode != 0:
                    logger.error(f"Failed to copy rule file:{src} to dest:{dest}")
                    return False

                spinner.success("Auto power saver installed successfully.")

                return True
