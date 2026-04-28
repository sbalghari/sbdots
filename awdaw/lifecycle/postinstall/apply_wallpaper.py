import subprocess
from time import sleep


def apply_wallpaper(logger, dry_run) -> bool:
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
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to apply wallpaper: {e}")
        return False
