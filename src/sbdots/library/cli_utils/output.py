from pyfiglet import figlet_format
from rich.text import Text
from rich.style import Style
from rich.console import Group
from rich.rule import Rule

from typing import Optional

from .console import CONSOLE, COLORS
from ._base import info, success, error, warning

# Gradient
HEADING_GRADIENT = [
    COLORS["red"],
    COLORS["blue"],
    COLORS["mauve"],
]


def print_newline(count: int = 1) -> None:
    CONSOLE.print("\n" * count, end="")


def print_rule(title: str = "SBDots") -> None:
    CONSOLE.print(Rule(title, style="primary"), justify="full")


def print_ascii_art(text: str, font: str = "slant") -> None:
    """Print ASCII art title with gradient effect"""
    ascii_art = figlet_format(text, font=font)
    lines = ascii_art.split("\n")
    styled_lines = []

    for i, line in enumerate(lines):
        if line.strip():
            # Create gradient effect
            gradient_idx = min(i // 2, len(HEADING_GRADIENT) - 1)
            style = Style(color=HEADING_GRADIENT[gradient_idx], bold=True)
            styled_lines.append(Text(line, style=style))

    _content = Group(*styled_lines)

    print_rule()
    CONSOLE.print(_content)


def print_header(t: str) -> None:
    CONSOLE.print(t, style="header")


def print_subheader(t: str) -> None:
    CONSOLE.print(t, style="subheader")


def print_text(t: str) -> None:
    CONSOLE.print(t, style="text")


def print_subtext(t: str) -> None:
    CONSOLE.print(t, style="subtext")


def print_info(
    t: str, *, details: Optional[str] = None, panel: bool = False
) -> None:
    CONSOLE.print(info(t, details=details, use_panel=panel))


def print_success(
    t: str, details: Optional[str] = None, panel: bool = False
) -> None:
    CONSOLE.print(success(t, details=details, use_panel=panel))


def print_error(
    t: str, details: Optional[str] = None, panel: bool = False
) -> None:
    CONSOLE.print(error(t, details=details, use_panel=panel))


def print_warning(
    t: str, details: Optional[str] = None, panel: bool = False
) -> None:
    CONSOLE.print(warning(t, details=details, use_panel=panel))
