from typing import List
import logging
import subprocess

from .run_cmd import run_command


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
        logger.error(f"Failed to install package: {package}. Exit code: {e.returncode}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error installing package: {package}: {e}")
        return False


def install_package_group(
    logger: logging.Logger, group: List[str], group_name: str
) -> bool:
    """Install a list of packages. Continues through failures, returns False if any fail."""
    logger.info(f"Installing package group: {group_name}")
    failed = []

    for package in group:
        if not install_package(logger=logger, package=package):
            logger.error(f"Failed to install package: {package}")
            failed.append(package)

    if failed:
        logger.error(
            f"Some packages failed in group: {group_name}: {', '.join(failed)}"
        )
        return False

    logger.info(f"All packages installed successfully in group: {group_name}")
    return True


def remove_package(logger: logging.Logger, package: str) -> bool:
    """Uninstall a package"""
    logger.info(f"Uninstalling package: {package}")

    # Check if package is installed or not
    if not is_installed(package):
        logger.info(f"Package not installed, skipping: {package}")
        return True

    try:
        result = run_command(["yay", "-R", package, "--noconfirm", "--quiet"])
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Failed to uninstall package: {package}. Exit code: {e.returncode}"
        )
        return False
    except Exception as e:
        logger.error(f"Unexpected error uninstalling package: {package}: {e}")
        return False
