from pathlib import Path
from time import sleep

from sbdots.core.fs_ops import path_lexists
from sbdots.core.security.sudo_keep_alive import SudoKeepAlive
from sbdots.core.system.sys_info import is_laptop, is_vm
from sbdots.core.command import run_sudo_cmd
from sbdots.cli.ui.cli_utils import print_header, Spinner


UDEV_RULES_DIR = Path("/etc/udev/rules.d")
UDEV_RULE_FILE = UDEV_RULES_DIR / "99-power-state.rules"
UDEV_RULE_FILE_CONTENT = '''SUBSYSTEM=="power_supply", ATTR{online}=="1", RUN+="/usr/local/bin/set_power_profile -b" \n
SUBSYSTEM=="power_supply", ATTR{online}=="0", RUN+="/usr/local/bin/set_power_profile -s"'''


class AutoPowerSaverInstaller:
    """
    Creates a udev rule to automatically toggle battery saver when a laptop is plugged in or unplugged.
    Additionally, it adjusts screen brightness: 50% when unplugged, 100% when plugged in.
    """

    @staticmethod
    def is_installed() -> bool:
        """Check if auto power saver udev rule is already installed"""
        return UDEV_RULE_FILE.exists()

    @staticmethod
    def install(logger, dry_run, verbose) -> bool:
        logger.info("Setting auto power saver.")

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
            with Spinner("Installing auto power saver...", verbose=verbose) as spinner:
                sleep(1)
                spinner.success("Auto power saver installed successfully.")

            return True

        with SudoKeepAlive() as sudo:
            if not sudo.is_running:
                logger.error("Failed to get sudo permissions, exiting...")
                return False

            with Spinner("Installing auto power saver...", verbose=verbose) as spinner:
                sleep(1)  # delay for better UX

                spinner.update_text("Copying udev rule file...")

                dest = Path("/etc/udev/rules.d")

                # Create dest if does not exists
                mkdir_cmd = ["sudo", "mkdir", "-p", dest]
                if not path_lexists(dest):
                    logger.debug(
                        f"Destination dir: {dest} doesn't exists, creating it."
                    )
                    result = run_sudo_cmd(
                        mkdir_cmd, logger=logger, spinner=spinner, verbose=verbose
                    )

                if not result:
                    spinner.fail("Failed to create udev rules directory.")
                    return False

                spinner.update_text("Preparing udev rule file...")

                tmp_file = "/tmp/99-power-state.rules"

                try:
                    with open(tmp_file, "w") as f:
                        f.write(UDEV_RULE_FILE_CONTENT)
                except Exception as e:
                    logger.error(f"Failed to write temp rule file: {e}")
                    spinner.fail("Failed to prepare udev rule file.")
                    return False

                spinner.update_text("Installing udev rule...")

                result = run_sudo_cmd(
                    ["sudo", "mv", tmp_file, str(UDEV_RULE_FILE)],
                    logger=logger,
                    spinner=spinner,
                    verbose=verbose,
                )

                if not result:
                    spinner.fail("Failed to install udev rule file.")
                    return False

                spinner.update_text("Setting permissions...")

                chmod_cmd = ["sudo", "chmod", "644", str(UDEV_RULE_FILE)]
                result = run_sudo_cmd(
                    chmod_cmd, logger=logger, spinner=spinner, verbose=verbose
                )

                if not result:
                    spinner.fail("Failed to set file permissions.")
                    return False

                spinner.update_text("Reloading udev rules...")

                reload_cmds = [
                    ["sudo", "udevadm", "control", "--reload-rules"],
                    ["sudo", "udevadm", "trigger"],
                ]

                for cmd in reload_cmds:
                    result = run_sudo_cmd(
                        cmd, logger=logger, spinner=spinner, verbose=verbose
                    )

                    if not result:
                        spinner.fail("Failed to reload udev rules.")
                        return False

                spinner.success("Auto power saver installed successfully.")
                logger.info("Auto power saver setup complete.")

                return True
