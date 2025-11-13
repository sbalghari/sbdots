import subprocess
from time import sleep


def reload_hyprland(dry_run) -> bool:
    if not dry_run:
        result = subprocess.run(
            ["hyprctl", "reload"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        sleep(1)
        return True

    return result.returncode == 0
