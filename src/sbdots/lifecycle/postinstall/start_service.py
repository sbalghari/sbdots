from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess

from sbdots.library.commands import run_command


def start_services(logger, dry_run) -> bool:
    logger.debug("Starting user services")

    if not _reload_user_systemd_daemon(logger, dry_run):
        return False

    logger.debug("Starting available user services")
    available_user_services = _get_available_services(Path("/usr/lib/systemd/user"))

    if not available_user_services:
        logger.debug("No user services found to start.")
    else:
        logger.debug(
            f"Found the following user services: {available_user_services}, starting them..."
        )

        for svc in available_user_services:
            if not start_user_service(logger, dry_run, svc):
                return False

    logger.debug("User services started successfully")

    return True


def start_user_service(logger, dry_run, service: str) -> bool:
    start_command: list[str] = [
        "systemctl",
        "--user",
        "start",
        "--now",
        service,
    ]
    logger.debug(f"Starting user service: {service}")
    if not dry_run:
        try:
            res: CompletedProcess = run_command(command=start_command)
        except Exception as exc:
            logger.error(f"Exception while starting service {service}: {exc}")
            return False

        if res.returncode != 0:
            logger.error(f"Failed to start service {service}")
            logger.debug(f"Enable command output: {res.stdout}")
            if getattr(res, "stderr", None):
                logger.debug(f"Enable command error: {res.stderr}")
            return False

    return True


def _reload_user_systemd_daemon(logger, dry_run) -> bool:
    logger.debug("Reloading systemd user daemon")

    if not dry_run:
        reload_command: list[str] = ["systemctl", "--user", "daemon-reload"]
        result: CompletedProcess = run_command(command=reload_command)

        if result.returncode != 0:
            logger.error("Failed to reload systemd user daemon")
            logger.debug(f"Command output: {result.stdout}")
            if result.stderr:
                logger.debug(f"Command error: {result.stderr}")
            return False

    logger.debug("Systemd user daemon reloaded successfully")
    return True


def _get_available_services(path: Path) -> list[str]:
    services_dir = path
    if not services_dir.is_dir():
        return []

    sbdots_services = [
        entry.name
        for entry in services_dir.iterdir()
        if entry.is_file()
        and entry.suffix == ".service"
        and entry.name.startswith("sbdots-")
    ]

    return sbdots_services
