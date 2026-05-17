import logging

from sbdots.constants import (
    USER_DOTFILES_DIR,
    USER_WALLPAPERS_DIR,
    SBDOTS_CONFIG_DIR,
    REQUIRED_DOTFILE_COMPONENTS,
)


def is_already_installed(logger: logging.Logger) -> bool:
    """
    Check whether SBDots is already installed by verifying the existence
    of key components and directories.
    """
    logger.info("Checking for existing SBDots installation")

    # Core existence checks
    checks: dict[str, bool] = {
        "Dotfiles directory": USER_DOTFILES_DIR.exists(),
        "Wallpapers directory": USER_WALLPAPERS_DIR.exists(),
        "SBDots config directory": SBDOTS_CONFIG_DIR.exists(),
    }

    # Log each check
    for name, exists in checks.items():
        status = "FOUND" if exists else "MISSING"
        logger.info(f"{name}: {status}")

    # Check if all user dotfile components exist
    dotfile_components_exist: bool = all(
        (USER_DOTFILES_DIR / component).exists()
        for component in REQUIRED_DOTFILE_COMPONENTS
    )

    logger.info(
        "Dotfile components check: "
        + ("ALL PRESENT" if dotfile_components_exist else "INCOMPLETE")
    )

    critical_paths_exist = (
        checks["Dotfiles directory"]
        and checks["Wallpapers directory"]
        and dotfile_components_exist
    )

    if critical_paths_exist:
        logger.info("SBDots appears to be already initialized.")
        return True

    logger.info("No existing initialization detected.")
    return False
