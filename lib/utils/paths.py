from pathlib import Path

HOME = Path.home()

# User dirs
USER_CONFIGS_DIR = HOME / ".config"
USER_DOTFILES_DIR = HOME / "Dotfiles"
USER_WALLPAPERS_DIR = HOME / "Wallpapers"
SBDOTS_CONFIG_DIR = HOME / ".config" / "sbdots"

# SBDots data dirs/files
SBDOTS_SHARE_DIR = Path("/usr/share/sbdots")
SBDOTS_DOTFILES_DIR = SBDOTS_SHARE_DIR / "dotfiles"
SBDOTS_WALLPAPERS_DIR = SBDOTS_SHARE_DIR / "wallpapers"
SBDOTS_UDEV_RULES_DIR = SBDOTS_SHARE_DIR / "udev_rules"
SBDOTS_METADATA_FILE = SBDOTS_SHARE_DIR / "metadata.json"

# System dirs
CUSTOM_UDEV_RULES_DIR = Path("/etc/udev/rules.d")

# SBDots packages(dependencies) list files
HYPRLAND_PKGS = SBDOTS_SHARE_DIR / "packages" / "hyprland.json"
CORE_PKGS = SBDOTS_SHARE_DIR / "packages" / "core.json"
FONTS = SBDOTS_SHARE_DIR / "packages" / "fonts.json"
APPLICATIONS = SBDOTS_SHARE_DIR / "packages" / "applications.json"
THEMING_PKGS = SBDOTS_SHARE_DIR / "packages" / "theming.json"
OPTIONAL_PKGS = SBDOTS_SHARE_DIR / "packages" / "optional.json"

# SBDots log dirs/files
SBDOTS_LOG_DIR = HOME / ".cache" / "sbdots" / "logs"

SBDOTS_NOTIFICATION_ICON: Path = Path.home() / "Downloads" / "SB." / "logo_light.svg"
