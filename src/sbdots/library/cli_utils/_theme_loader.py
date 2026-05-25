from rich.theme import Theme

from sbdots.library.exceptions import ThemeConfigError
from sbdots.library.config_utils import read_rich_theme
from sbdots.constants import DEFAULT_RICH_THEME_PATH, USER_RICH_THEME_PATH


def load_theme() -> tuple[Theme, dict, dict]:
    # TODO: Implement fallback if user's theme file is invalid or incomplete
    if USER_RICH_THEME_PATH.exists():
        path = USER_RICH_THEME_PATH
    else:
        path = DEFAULT_RICH_THEME_PATH

    config = read_rich_theme(path)

    colors = config.get("colors", {})
    styles = config.get("styles", {})
    icons = config.get("icons", {})

    if not colors or not styles or not icons:
        raise ThemeConfigError("Theme must define [colors], [styles] and [icons]")

    return Theme(styles), colors, icons
