"""
Global constants for the SBDots project.

This module centralizes all constant definitions used throughout the application,
including paths, configuration sections, UI messages, timeouts, and other magic values.
"""

from pathlib import Path
from typing import Callable, Any, TypeAlias, Union
from enum import Enum
import re
import os

# =============================================================================
# DIRECTORY PATHS
# =============================================================================
HOME = Path.home()
USER_CONFIGS_DIR = HOME / ".config"
USER_DOTFILES_DIR = HOME / "Dotfiles"
USER_WALLPAPERS_DIR = HOME / "Wallpapers"
USER_THEME_PATH = USER_CONFIGS_DIR / "rich" / "theme.toml"
SBDOTS_CONFIG_DIR = HOME / ".sbdots"
SBDOTS_DATA_DIR = HOME / ".local" / "share" / "sbdots"
SBDOTS_STATE_DIR = (
    Path(os.environ.get("XDG_STATE_HOME", HOME / ".local/state")) / "sbdots"
)
SBDOTS_DOTFILES_DIR = HOME / ".local" / "share" / "sbdots" / ".config"
SBDOTS_WALLPAPERS_DIR = SBDOTS_DATA_DIR / "wallpapers"
SBDOTS_LOG_DIR = SBDOTS_STATE_DIR / "logs"
DEFAULT_THEME_PATH = Path("/etc") / "sbdots" / "rich_theme.toml"


# =============================================================================
# DAEMON CONFIGURATION
# =============================================================================
# Clipboard listener configuration
CACHE_FILE = SBDOTS_STATE_DIR / "cliphist"
MAX_ENTRIES = 50
MAX_LENGTH = 200
POLL_SEC = 0.2

# Actions daemon configuration
SOCKET_PATH = "/tmp/sbdots_actions.sock"
ACTION_TIMEOUT = 30  # seconds

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 3


class LogLevel(Enum):
    """Log levels for the application."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# =============================================================================
# COMPONENTS
# =============================================================================
REQUIRED_DOTFILE_COMPONENTS = [
    "hypr",
    "waybar",
    "rofi",
    "fish",
    "kitty",
    "neofetch",
    "fastfetch",
    "cava",
    "waypaper",
    "swaync",
    "btop",
    "systemd",
    "wlogout",
    "atuin",
    "starship.toml",
]

OPTIONAL_PACKAGES = [
    "visual-studio-code-bin",
    "vlc",
    "smile",
    "sddm",
    "obs-studio",
    "mission-center",
    "loupe",
    "libreoffice-fresh",
    "gnome-text-editor",
    "ark",
]

# =============================================================================
# CONFIGURATION SECTIONS
# =============================================================================
DEFAULT_SECTION = "core"
WEATHER_SECTION = "Weather"
HYPRSHADE_SECTION = "Hyprshade"
WAYBAR_SECTION = "Waybar"

# =============================================================================
# INSTALLER UI MESSAGES
# =============================================================================
WELCOME_MESSAGE = "Welcome to SBDots initializer!"
SETUP_DESCRIPTION = "This setup will copy sbdots files to the respective user dirs and apply settings."
DRY_RUN_MESSAGE = "Dry-run mode enabled. No changes will be made."
VERBOSE_MESSAGE = "Verbose mode enabled. Might be noisy."

ALREADY_INSTALLED_MESSAGE = "SBDots is already initialized."
ALREADY_INSTALLED_DETAILS = "If you want to reinitialize or repair, please remove existing files first."

INSTALLATION_CANCELLED_MESSAGE = "SBDots initialization cancelled!"
INSTALLATION_CANCELLED_DETAILS = (
    "If you want to initialize SBDots, please run 'sbdots init'."
)

INSTALLATION_SUCCESS_MESSAGE = "SBDots initialization completed successfully!"
INSTALLATION_SUCCESS_DETAILS = "Please restart your PC once before using..."

INSTALLATION_FAILED_MESSAGE = (
    "SBDots initialization failed. Please check the logs for details"
)
INSTALLATION_FAILED_COMPONENTS_HEADER = (
    "The following components failed to initialize:"
)

CONFIRMATION_MESSAGE = "Do you want to start the initialization?"

FINALIZATION_HEADER = "Finalizing initialization:"

# =============================================================================
# WEATHER DATA ICONS
# =============================================================================
# Map: WeatherAPI.com condition codes > Nerd Fonts icons
WEATHER_ICONS: dict[int, str] = {
    1000: "󰖨",  # Sunny
    1003: "󰖕",  # Partly cloudy
    1006: "󰖐",  # Cloudy
    1009: "󰖑",  # Overcast
    1030: "󰖑",  # Mist
    1063: "󰼳",  # Patchy rain possible
    1066: "󰼴",  # Patchy snow possible
    1069: "󰙿",  # Patchy sleet possible
    1072: "󰙿",  # Patchy freezing drizzle possible
    1087: "󰙾",  # Thundery outbreaks possible
    1114: "󰼶",  # Blowing snow
    1117: "󰼶",  # Blizzard
    1135: "󰖑",  # Fog
    1147: "󰖑",  # Freezing fog
    1150: "󰖗",  # Patchy light drizzle
    1153: "󰖗",  # Light drizzle
    1168: "󰖗",  # Freezing drizzle
    1171: "󰖗",  # Heavy freezing drizzle
    1180: "󰖗",  # Patchy light rain
    1183: "󰖗",  # Light rain
    1186: "󰖗",  # Moderate rain at times
    1189: "󰖗",  # Moderate rain
    1192: "󰖗",  # Heavy rain at times
    1195: "󰖗",  # Heavy rain
    1198: "󰖗",  # Light freezing rain
    1201: "󰖗",  # Moderate or heavy freezing rain
    1204: "󰙿",  # Light sleet
    1207: "󰙿",  # Moderate or heavy sleet
    1210: "󰼶",  # Patchy light snow
    1213: "󰼶",  # Light snow
    1216: "󰼶",  # Moderate snow
    1219: "󰼶",  # Heavy snow
    1222: "󰙿",  # Ice pellets
    1225: "󰙿",  # Light ice pellets
    1237: "󰙿",  # Moderate or heavy ice pellets
    1240: "󰖗",  # Light rain shower
    1243: "󰖗",  # Moderate or heavy rain shower
    1246: "󰖗",  # Torrential rain shower
    1249: "󰙿",  # Light sleet showers
    1252: "󰙿",  # Moderate or heavy sleet showers
    1255: "󰼶",  # Light snow showers
    1258: "󰼶",  # Moderate or heavy snow showers
    1261: "󰙿",  # Light showers of ice pellets
    1264: "󰙿",  # Moderate or heavy showers of ice pellets
    1273: "󰙾",  # Patchy light rain with thunder
    1276: "󰙾",  # Moderate or heavy rain with thunder
    1279: "󰙾",  # Patchy light snow with thunder
    1282: "󰙾",  # Moderate or heavy snow with thunder
}

# =============================================================================
# CLI DISPLAY CONFIGURATION
# =============================================================================
# Note: HEADING_GRADIENT is defined in library/cli_utils/output.py as it requires
# runtime access to COLORS dict from the theme loader
# REGULAR EXPRESSIONS
# =============================================================================
# Pattern for resolving configuration placeholders
PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][\w]*)\.([^\|}]+)(?:\|([^\}]+))?\}")

# Patterns for detecting sudo prompts in command output
SUDO_PROMPT_PATTERNS = [
    re.compile(r"\[sudo\] password for .*:"),  # sudo password query prompt
    re.compile(
        r"Sorry, try again\.\s*\[sudo\] password for .*:"
    ),  # sudo retry password prompt
    re.compile(
        r"sudo: \d+ incorrect password attempts"
    ),  # sudo no password attempts left prompt
    re.compile(
        r"sudo: timed out reading password"
    ),  # sudo password query timeout prompt
]

# =============================================================================
# TYPE ALIASES
# =============================================================================
COMMAND: TypeAlias = Union[list[Any], str]
FinalizationStep: TypeAlias = tuple[str, Callable[[], bool], bool]
