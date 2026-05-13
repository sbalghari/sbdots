import subprocess
from time import sleep


def reload_hyprland(dry_run) -> bool:
    if dry_run:
        sleep(1)
        return True

    result = subprocess.run(
        ["hyprctl", "reload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0
