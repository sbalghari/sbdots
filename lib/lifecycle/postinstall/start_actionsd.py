from library import run_command
from utils.logger import Logger
from typing import List
from subprocess import CompletedProcess


def start_actionsd(logger: Logger, dry_run) -> bool:
    logger.debug("Starting actions daemon service")

    if not _reload_systemd_daemon(logger, dry_run):
        return False

    if not _enable_actionsd(logger, dry_run):
        return False

    logger.info("Successfully started actions daemon service")
    return True


def _reload_systemd_daemon(logger: Logger, dry_run) -> bool:
    logger.debug("Reloading systemd user daemon")

    if not dry_run:
        reload_command: List[str] = ["systemctl", "--user", "daemon-reload"]
        result: CompletedProcess = run_command(command=reload_command)

        if result.returncode != 0:
            logger.error("Failed to reload systemd daemon")
            logger.debug(f"Command output: {result.stdout}")
            if result.stderr:
                logger.debug(f"Command error: {result.stderr}")
            return False

    logger.debug("Systemd daemon reloaded successfully")
    return True


def _enable_actionsd(logger: Logger, dry_run) -> bool:
    logger.debug("Enabling and starting actions daemon service")

    if not dry_run:
        enable_command: List[str] = [
            "systemctl",
            "--user",
            "enable",
            "--now",
            "sbdots-actionsd.service",
        ]
        result: CompletedProcess = run_command(command=enable_command)

        if result.returncode != 0:
            logger.error("Failed to enable and start sbdots-actionsd.service")
            logger.debug(f"Command output: {result.stdout}")
            if result.stderr:
                logger.debug(f"Command error: {result.stderr}")
            return False

    logger.debug("Service enabled and started successfully")
    return True
