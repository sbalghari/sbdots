from pathlib import Path
from time import sleep

from sbdots.library.fs_ops import path_lexists
from sbdots.library.sudo_keep_alive import SudoKeepAlive
from sbdots.library.sys_info import is_laptop, is_vm
from sbdots.library.commands import run_sudo_cmd
from sbdots.library.cli_utils import print_header, Spinner


UDEV_RULES_DIR = Path("/etc/udev/rules.d")
UDEV_RULE_FILE = UDEV_RULES_DIR / "99-power-state.rules"
UDEV_RULE_FILE_CONTENT = (
    'SUBSYSTEM=="power_supply", ATTR{online}=="1", '
    'RUN+="/usr/local/bin/set_power_profile -b" \n'
    'SUBSYSTEM=="power_supply", ATTR{online}=="0", '
    'RUN+="/usr/local/bin/set_power_profile -s"'
)


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
                # Create temporary file first
                tmp_file = Path("/tmp/99-power-state.rules")

                try:
                    # Write content to temp file
                    tmp_file.write_text(UDEV_RULE_FILE_CONTENT)
                    # Set proper permissions on temp file
                    tmp_file.chmod(0o644)
                except Exception as e:
                    logger.error(f"Failed to write temp rule file: {e}")
                    spinner.error("Failed to prepare udev rule file.")
                    return False

                # Create destination directory if it doesn't exist
                if not path_lexists(UDEV_RULES_DIR):
                    spinner.update_text("Creating udev rules directory...")
                    mkdir_cmd = ["mkdir", "-p", str(UDEV_RULES_DIR)]
                    result = run_sudo_cmd(
                        mkdir_cmd,
                        logger=logger,
                        spinner=spinner,
                        verbose=verbose,
                    )

                    if not result:
                        spinner.error("Failed to create udev rules directory.")
                        # Cleanup temp file
                        try:
                            tmp_file.unlink()
                        except:  # noqa: E722
                            pass
                        return False

                # Move temp file to destination
                spinner.update_text("Installing udev rule...")
                mv_cmd = ["mv", str(tmp_file), str(UDEV_RULE_FILE)]
                result = run_sudo_cmd(
                    mv_cmd,
                    logger=logger,
                    spinner=spinner,
                    verbose=verbose,
                )

                if not result:
                    spinner.error("Failed to install udev rule file.")
                    # Cleanup temp file if still exists
                    try:
                        if tmp_file.exists():
                            tmp_file.unlink()
                    except:  # noqa: E722
                        pass
                    return False

                # Verify the rule was installed correctly
                try:
                    if not UDEV_RULE_FILE.exists():
                        spinner.error("Rule file not found after installation.")
                        return False

                    installed_content = UDEV_RULE_FILE.read_text()
                    if installed_content != UDEV_RULE_FILE_CONTENT:
                        logger.error(
                            "Installed rule content doesn't match expected content."
                        )
                        spinner.error("Rule file content verification failed.")
                        return False
                except Exception as e:
                    logger.error(f"Failed to verify installation: {e}")
                    spinner.error("Installation verification failed.")
                    return False

                spinner.success("Auto power saver installed successfully.")
                logger.info("Auto power saver setup complete.")
                return True
