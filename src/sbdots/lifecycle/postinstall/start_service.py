from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess

from sbdots.library.commands import run_command


def start_services(logger, dry_run) -> bool:
    logger.debug("Starting user services")

    if not _reload_user_systemd_daemon(logger, dry_run):
        return False

    logger.debug("Starting available user services")
    available_user_services = _get_available_user_services()

    if not available_user_services:
        logger.debug("No user services found to start.")
    else:
        logger.debug(
            f"Found the following user services: {available_user_services}, starting them..."
        )

        for svc in available_user_services:
            if not _enable_and_start_user_service(logger, dry_run, svc):
                return False

    logger.debug("User services started successfully")

    # Check for system services
    available_system_services = _get_available_system_services()
    if available_system_services:
        logger.info(
            "System services are available but require root privileges to enable/start."
        )
        logger.info("To enable system services, run:")
        for svc in available_system_services:
            logger.info(f"  sudo systemctl enable --now {svc}")

    return True


def _enable_and_start_user_service(logger, dry_run, service: str) -> bool:
    enable_command: list[str] = [
        "systemctl",
        "--user",
        "enable",
        "--now",
        service,
    ]
    logger.debug(f"Enabling and starting user service {service}")
    if not dry_run:
        try:
            res: CompletedProcess = run_command(command=enable_command)
        except Exception as exc:
            logger.error(f"Exception while enabling/starting service {service}: {exc}")
            return False

        if res.returncode != 0:
            logger.error(f"Failed to enable/start service {service}")
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


def _get_available_user_services() -> list[str]:
    services_dir = Path("/usr/lib/systemd/user")
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


def _get_available_system_services() -> list[str]:
    services_dir = Path("/usr/lib/systemd/system")
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
