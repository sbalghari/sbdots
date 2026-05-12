from pathlib import Path

HOME = Path.home()

# User dirs
USER_CONFIGS_DIR = HOME / ".config"
USER_DOTFILES_DIR = HOME / "Dotfiles"
USER_WALLPAPERS_DIR = HOME / "Wallpapers"
SBDOTS_CONFIG_DIR = HOME / ".sbdots"
SBDOTS_SETTINGS_DIR = SBDOTS_CONFIG_DIR / "settings"
SBDOTS_STATE_DIR = HOME / ".local" / "state" / "sbdots"

# SBDots data dirs/files
SBDOTS_SHARE_DIR = Path("/usr/share/sbdots")
SBDOTS_DOTFILES_DIR = SBDOTS_SHARE_DIR / ".config"
SBDOTS_WALLPAPERS_DIR = SBDOTS_SHARE_DIR / ".sbdots" / "wallpapers"

SBDOTS_NOTIFICATION_ICON: Path = Path.home() / "Downloads" / "SB." / "logo_light.svg"
