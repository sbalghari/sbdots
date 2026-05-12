from pyfiglet import figlet_format
from rich.console import Console
from rich.text import Text as RichText
from rich.live import Live as RichLive
from rich.spinner import Spinner as RichSpinner
from rich.style import Style as RichStyle
from rich.console import Group
from rich.panel import Panel
from rich.box import ROUNDED
from rich.rule import Rule
from rich.align import Align, AlignMethod
from rich.prompt import Prompt, Confirm
from InquirerPy.prompts.checkbox import CheckboxPrompt
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.utils import InquirerPyStyle
from typing import Optional

from sbdots.cli.ui.console import CONSOLE
from sbdots.utils.types import INPUT_VALIDATOR

__all__ = [
    "Spinner",
    "print_ascii_title",
    "print_header",
    "print_subtext",
    "print_info",
    "print_success",
    "print_error",
    "print_warning",
    "confirm",
    "rinput",
    "clear_console",
    "clear_console_v",
    "get_console",
    "print_banner",
    "print_newline",
    "print_rule",
    "check_box",
    "select",
]

# Colors palette
HEADER_COLOR = "#6C63FF"  # indigo glow
PRIMARY_COLOR = "#FF6584"  # warm neon rose
SECONDARY_COLOR = "#4ADE80"  # mellow green
ACCENT_COLOR = "#FACC15"  # soft gold highlight
ERROR_COLOR = "#EF476F"  # vivid raspberry
SUCCESS_COLOR = "#3BCF93"  # soothing aqua-green
WARNING_COLOR = "#FBBF24"  # muted amber
INFO_COLOR = "#38BDF8"  # bright sky cyan
SUB_TEXT_COLOR = "#A5ACC1"  # gentle desaturated text
MUTED_COLOR = "#4B5563"  # slate gray
HIGHLIGHT_COLOR = "#F3F4F6"  # clean off-white
SELECTION_COLOR = "#3730A3"  # deep royal blue

# Gradients
HEADING_GRADIENT = [
    HEADER_COLOR,
    PRIMARY_COLOR,
    ACCENT_COLOR,
]


# Characters
DONE_ICON: str = "󰄴"
WARNING_ICON: str = ""
ERROR_ICON: str = ""
INFO_ICON: str = ""
CHECK_ICON: str = DONE_ICON
CHECKBOX_ICON: str = "󰋙"
CHECKBOX_CHECKED_ICON: str = "󰫈"
QUESTION_MARK: str = ""
POINTER_ICON: str = ""

# Styles
HEADING_STYLE = RichStyle(color=HEADER_COLOR, bold=True)
SUB_HEADING_STYLE = RichStyle(color=PRIMARY_COLOR, bold=True, italic=True)
TEXT_STYLE = RichStyle(color=HIGHLIGHT_COLOR)
SUBTEXT_STYLE = RichStyle(color=SUB_TEXT_COLOR, dim=True)
ERROR_STYLE = RichStyle(color=ERROR_COLOR, bold=True)
SUCCESS_STYLE = RichStyle(color=SUCCESS_COLOR, bold=True)
WARNING_STYLE = RichStyle(color=WARNING_COLOR, bold=True)
INFO_STYLE = RichStyle(color=INFO_COLOR, italic=True)
ACCENT_STYLE = RichStyle(color=ACCENT_COLOR, bold=True)

INQUIREPY_STYLE = InquirerPyStyle(
    {
        "answer": HEADER_COLOR,
        "input": PRIMARY_COLOR,
        "question": SUB_TEXT_COLOR,
        "instruction": SUB_TEXT_COLOR,
        "long_instruction": SUB_TEXT_COLOR,
        "pointer": PRIMARY_COLOR,
        "checkbox": SECONDARY_COLOR,
        "separator": MUTED_COLOR,
        "skipped": MUTED_COLOR,
        "validator": ERROR_COLOR,
        "marker": PRIMARY_COLOR,
    }
)


class Spinner:
    """Context manager for showing a live console spinner."""

    def __init__(self, message: str, spinner_type: str = "dots", verbose: bool = False):
        self.message = message
        self.spinner_style = spinner_type
        self.verbose = verbose

        self.spinner = RichSpinner(
            self.spinner_style, text=self._styled_text(message), style=TEXT_STYLE
        )
        self.live = RichLive(
            Panel(
                self.spinner,
                title="[bold]Processing[/bold]",
                border_style=PRIMARY_COLOR,
                box=ROUNDED,
                width=60,
            ),
            refresh_per_second=60,
            console=CONSOLE,
            transient=True,
        )

    def _styled_text(self, text: str) -> RichText:
        return RichText(text, style=TEXT_STYLE)

    def update_text(self, new_message: str) -> None:
        """Update the spinner text"""
        self.spinner.update(text=self._styled_text(new_message))

    def success(self, message: str, details: Optional[str] = None) -> None:
        """Show success message in a panel"""
        content = RichText(DONE_ICON + " " + message, style=SUCCESS_STYLE)
        if details:
            content.append("\n")
            content.append(RichText(details, style=SUBTEXT_STYLE))
        if not self.verbose:
            self.live.update(
                Panel(
                    content,
                    title="[bold]Success[/bold]",
                    border_style=SUCCESS_COLOR,
                    box=ROUNDED,
                    width=60,
                )
            )
        else:
            CONSOLE.print(message)
            if details:
                CONSOLE.print(details)

    def error(
        self, message: str, details: Optional[str] = None, stop: bool = False
    ) -> None:
        """Show error message in a panel"""
        content = RichText(ERROR_ICON + " " + message, style=ERROR_STYLE)
        if details:
            content.append("\n")
            content.append(RichText(details, style=SUBTEXT_STYLE))
        if not self.verbose:
            self.live.update(
                Panel(
                    content,
                    title="[bold]Error[/bold]",
                    border_style=ERROR_COLOR,
                    box=ROUNDED,
                    width=60,
                )
            )
            if stop:
                self.live.stop()
        else:
            CONSOLE.print(message)
            if details:
                CONSOLE.print(details)

    def warning(self, message: str, details: Optional[str] = None) -> None:
        """Show warning message in a panel"""
        content = RichText(WARNING_ICON + " " + message, style=WARNING_STYLE)
        if details:
            content.append("\n")
            content.append(RichText(details, style=SUBTEXT_STYLE))
        if not self.verbose:
            self.live.update(
                Panel(
                    content,
                    title="[bold]Warning[/bold]",
                    border_style=WARNING_COLOR,
                    box=ROUNDED,
                    width=60,
                )
            )
        else:
            CONSOLE.print(message)
            if details:
                CONSOLE.print(details)

    def get_password(self) -> str:
        renderable = self.live.get_renderable()
        self.live.update("")

        pw = rinput(prompt="[SUDO] Enter your password: ", password=True)

        self.live.update(renderable)

        return pw

    def __enter__(self):
        if not self.verbose:
            self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.verbose:
            self.live.stop()


def print_ascii_title(text: str, font: str = "slant") -> None:
    """Print ASCII art title with gradient effect"""
    ascii_art = figlet_format(text, font=font)
    lines = ascii_art.split("\n")
    styled_lines = []

    for i, line in enumerate(lines):
        if line.strip():
            # Create gradient effect
            gradient_idx = min(i // 2, len(HEADING_GRADIENT) - 1)
            style = RichStyle(color=HEADING_GRADIENT[gradient_idx], bold=True)
            styled_lines.append(RichText(line, style=style))

    panel_content = Group(*styled_lines)

    print_rule()
    CONSOLE.print(panel_content)


def print_header(
    text: str, icon: Optional[str] = None, details: Optional[str] = None
) -> None:
    """Print header with optional icon"""
    header_text = RichText()
    if icon:
        header_text.append(f"{icon} ", style=ACCENT_STYLE)
    header_text.append(text, style=HEADING_STYLE)

    content = text

    content = Group(
        RichText(f"{text}", style=HEADING_STYLE),
        *([RichText(f"  ↳ {details}", style=SUBTEXT_STYLE)] if details else []),
    )
    CONSOLE.print(content)


def print_subtext(text: str, align: AlignMethod = "left") -> None:
    """Print subtext with alignment"""
    aligned_text = Align(RichText(text, style=SUBTEXT_STYLE), align)
    CONSOLE.print(aligned_text)


def print_info(text: str, details: Optional[str] = None) -> None:
    """Print info message with optional details"""
    content = Group(
        RichText(f"{INFO_ICON} {text}", style=INFO_STYLE),
        *([RichText(f"  ↳ {details}", style=SUBTEXT_STYLE)] if details else []),
    )
    CONSOLE.print(content)


def print_success(text: str, details: Optional[str] = None) -> None:
    """Print success message with optional details"""
    content = Group(
        RichText(f"{DONE_ICON} {text}", style=SUCCESS_STYLE),
        *([RichText(f"  ↳ {details}", style=SUBTEXT_STYLE)] if details else []),
    )
    CONSOLE.print(Panel(content, border_style=SUCCESS_COLOR, box=ROUNDED, width=60))


def print_error(text: str, details: Optional[str] = None) -> None:
    """Print error message with optional details"""
    content = Group(
        RichText(f"{ERROR_ICON} {text}", style=ERROR_STYLE),
        *([RichText(f"  ↳ {details}", style=SUBTEXT_STYLE)] if details else []),
    )
    CONSOLE.print(Panel(content, border_style=ERROR_COLOR, box=ROUNDED, width=60))


def print_warning(text: str, details: Optional[str] = None) -> None:
    """Print warning message with optional details"""
    content = Group(
        RichText(f"{WARNING_ICON} {text}", style=WARNING_STYLE),
        *([RichText(f"  ↳ {details}", style=SUBTEXT_STYLE)] if details else []),
    )
    CONSOLE.print(Panel(content, border_style=WARNING_COLOR, box=ROUNDED, width=60))


def confirm(message: str = "Confirm?", default_yes: bool = False) -> bool:
    """Ask yes/No using Rich Confirm prompt"""
    try:
        # Create custom styled confirm prompt
        prompt_text = f"[bold]{message}[/bold] [dim](y/n)[/dim]"
        if default_yes:
            prompt_text += " [green][default: y][/green]"
        else:
            prompt_text += " [red][default: n][/red]"

        CONSOLE.print(prompt_text)

        # Use rich's Confirm with custom styling
        result = Confirm.ask(
            "", console=CONSOLE, default=default_yes, show_default=True
        )

        return result

    except KeyboardInterrupt:
        CONSOLE.print("\n[dim]Cancelled[/dim]")
        return False


def rinput(
    prompt: str,
    password: bool = False,
    validator: Optional[INPUT_VALIDATOR] = None,
    validation_instruction: Optional[str] = None,
) -> str:
    """Ask the user to input something using Rich prompt"""

    # Create styled prompt
    prompt_text = f"[bold]{prompt}[/bold]"

    CONSOLE.print(prompt_text)

    def _base_validator(validator: Optional[INPUT_VALIDATOR]):
        base: bool = len(user_input) > 0
        if not validator:
            return not base
        return base and validator(user_input)

    while True:
        try:
            if password:
                # getpass for password inputs
                import getpass

                user_input = getpass.getpass("")
            else:
                # Rich Prompt for regular input
                user_input = Prompt.get_input(
                    console=CONSOLE, prompt="", password=password
                )

            # Validate
            if _base_validator(validator):
                if not validator and not validation_instruction:
                    print_error(text="Invalid input!", details="Input can't be empty.")
                    continue
                print_error(text="Invalid input!", details=validation_instruction)
                continue

            if user_input:
                return user_input

        except KeyboardInterrupt:
            CONSOLE.print("\n[dim]Cancelled[/dim]")
            return ""


def clear_console() -> None:
    """Reset console"""
    CONSOLE.print("\033c", end="")


def clear_console_v() -> None:
    """Clear visible console"""
    CONSOLE.clear()


def get_console() -> Console:
    """Get console instance"""
    return CONSOLE


def print_banner(text: str, style: RichStyle = ACCENT_STYLE) -> None:
    """Print a banner-style message"""
    banner = f"╭{'─' * (len(text) + 4)}╮\n│  {text}  │\n╰{'─' * (len(text) + 4)}╯"
    CONSOLE.print(RichText(banner, style=style), justify="center")


def print_newline(count: int = 1) -> None:
    """Print newlines"""
    CONSOLE.print("\n" * count, end="")


def print_rule(title: str | RichText = "SBDots", style: str = PRIMARY_COLOR) -> None:
    """Print a horizontal rule"""
    CONSOLE.print(Rule(title, style=style), justify="full")


def check_box(choices: list, message: str = "Select items:") -> list:
    """Choose one or multiple items from a list"""
    print_header(message, details="Press Enter with no selection to skip")

    chosen = CheckboxPrompt(
        message="",
        style=INQUIREPY_STYLE,
        choices=choices,
        qmark="",
        amark="",
        cycle=True,
        pointer=POINTER_ICON,
        show_cursor=False,
        disabled_symbol=CHECKBOX_ICON,
        enabled_symbol=CHECKBOX_CHECKED_ICON,
        transformer=lambda result: "",
        long_instruction="󱁐 / Space: toggle, ↑↓ / Arrow keys: navigate, 󰌑 / Enter: confirm",
    ).execute()

    return chosen


def select(choices: list, message: str = "Select items:") -> str:
    """Choose one items from a list"""
    print_header(message)

    selected = ListPrompt(
        message="",
        style=INQUIREPY_STYLE,
        choices=choices,
        qmark="",
        amark="",
        cycle=True,
        pointer=POINTER_ICON,
        show_cursor=False,
        transformer=lambda result: "",
        long_instruction="↑↓ / Arrow keys: navigate, 󰌑 / Enter: confirm",
    ).execute()

    return selected
