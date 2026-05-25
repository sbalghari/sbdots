from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess

from sbdots.library.commands import run_command


def start_services(logger, dry_run) -> bool:
    logger.debug("Starting user services")

    if not _reload_systemd_daemon(logger, dry_run):
        return False

    logger.debug("Starting available services")
    available_services = _get_available_services()

    if not available_services:
        logger.debug("No user services found to start.")
        return True

    logger.debug(
        f"Found the following services: {available_services}, starting them..."
    )

    for svc in available_services:
        start_command: list[str] = [
            "systemctl",
            "--user",
            "start",
            "--now",
            svc,
        ]
        logger.debug(f"Starting service {svc}")
        if not dry_run:
            try:
                res: CompletedProcess = run_command(command=start_command)
            except Exception as exc:
                logger.error(f"Exception while starting service {svc}: {exc}")
                return False

            if res.returncode != 0:
                logger.error(f"Failed to start service {svc}")
                logger.debug(f"Start command output: {res.stdout}")
                if getattr(res, "stderr", None):
                    logger.debug(f"Start command error: {res.stderr}")
                return False

    logger.debug("All services started successfully")
    return True


def _reload_systemd_daemon(logger, dry_run) -> bool:
    logger.debug("Reloading systemd user daemon")

    if not dry_run:
        reload_command: list[str] = ["systemctl", "--user", "daemon-reload"]
        result: CompletedProcess = run_command(command=reload_command)

        if result.returncode != 0:
            logger.error("Failed to reload systemd daemon")
            logger.debug(f"Command output: {result.stdout}")
            if result.stderr:
                logger.debug(f"Command error: {result.stderr}")
            return False

    logger.debug("Systemd daemon reloaded successfully")
    return True


def _get_available_services() -> list[str]:
    services_dir = Path.home() / ".config" / "systemd" / "user"
    if not services_dir.is_dir():
        return []

    return [
        entry.name
        for entry in services_dir.iterdir()
        if entry.is_file() and entry.suffix == ".service"
    ]
