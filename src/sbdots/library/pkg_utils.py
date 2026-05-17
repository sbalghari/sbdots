import logging
import subprocess

from .commands import run_command


def is_installed(package: str) -> bool:
    """Check if a package is installed using pacman."""
    result = run_command(["pacman", "-Qq", package])
    return result.returncode == 0


def install_package(logger: logging.Logger, package: str) -> bool:
    """Install a package with yay."""
    logger.info(f"Installing package: {package}")

    # Check if package is installed or not
    if is_installed(package):
        logger.info(f"Package already installed, skipping: {package}")
        return True

    try:
        result = run_command(["yay", "-S", package, "--noconfirm", "--quiet"])
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Failed to install package: {package}. Exit code: {e.returncode}"
        )
        return False
    except Exception as e:
        logger.error(f"Unexpected error installing package: {package}: {e}")
        return False
