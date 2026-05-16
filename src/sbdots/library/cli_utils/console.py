from rich.console import Console

from ._theme_loader import load_theme


_THEME, COLORS, ICONS = load_theme()

CONSOLE = Console(theme=_THEME)


def reset_console() -> None:
    """Reset console"""
    CONSOLE.print("\033c", end="")


def clear_console() -> None:
    """Clear visible console"""
    CONSOLE.clear()


def get_console() -> Console:
    """Return the CONSOLE"""
    return CONSOLE
