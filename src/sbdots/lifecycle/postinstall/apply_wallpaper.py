import subprocess
from time import sleep
import logging

from sbdots.library.command import notify_send


def apply_wallpaper(logger: logging.Logger, dry_run) -> bool:
    """Apply wallpaper using waypaper."""
    try:
        if not dry_run:
            subprocess.run(
                ["waypaper", "--restore"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            sleep(1)

        logger.info("Wallpaper applied successfully.")
        return True
    except subprocess.CalledProcessError:
        notify_send(
            "SBDots Postinstall",
            body="post-install hook 'apply_wallpaper' failed; try running 'waypaper --random'. if error presists, feel free to open an issue on gituhub with the logfile.",
            urgency="critical",
            expire_time=5,
        )
        logger.exception("Failed to apply wallpaper: ")
        return False
