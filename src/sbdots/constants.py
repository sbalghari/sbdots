"""
Global constants for SBDots.

This module centralizes all constant definitions used throughout,
including paths, configuration sections, and other values.
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

SBDOTS_CONFIG_DIR = HOME / ".sbdots"
SBDOTS_DATA_DIR = Path("/usr/share/sbdots")
SBDOTS_STATE_DIR = (
    Path(os.environ.get("XDG_STATE_HOME", HOME / ".local" / "state")) / "sbdots"
)

SBDOTS_DOTFILES_DIR = SBDOTS_DATA_DIR / "configs"
SBDOTS_WALLPAPERS_DIR = SBDOTS_DATA_DIR / "wallpapers"
SBDOTS_LOG_DIR = SBDOTS_STATE_DIR / "logs"

DEFAULT_RICH_THEME_PATH = Path("/etc") / "sbdots" / "rich_theme.toml"
USER_RICH_THEME_PATH = USER_CONFIGS_DIR / "rich" / "theme.toml"


# =============================================================================
# DAEMON CONFIGURATION
# =============================================================================
# Actions daemon
VALID_ACTIONS: list[str] = [
    "get_available_updates",
    "get_hypridle_status",
    "get_weather_data",
    "on_wallpaper_change",
    "toggle_hypridle",
]

# Clipboard listener configuration
CACHE_FILE = SBDOTS_STATE_DIR / "cliphist"
MAX_ENTRIES = 50
MAX_LENGTH = 200
POLL_SEC = 0.2


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
    "freedownloadmanager-bin",
    "loupe",
    "libreoffice-fresh",
    "gnome-text-editor",
    "ark",
]

# =============================================================================
# CONFIGURATION SECTIONS
# =============================================================================
DEFAULT_SECTION = "core"
WEATHER_SECTION = "weather"
WAYBAR_SECTION = "waybar"
MATUGEN_SECTION = "matugen"

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
LifeCycleStep: TypeAlias = tuple[str, Callable[[], bool], bool]
