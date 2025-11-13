import sys
import tty
import termios

from pyfiglet import figlet_format
from rich.text import Text as RichText
from rich.live import Live as RichLive
from rich.spinner import Spinner as RichSpinner
from rich.style import Style as RichStyle
from rich.console import Console
from rich.prompt import Prompt
from typing import List, Set, Union


# Colors
HEADER_COLOR: str = "#1e66f5"
PRIMARY_COLOR: str = "#8839ef"
ERROR_COLOR: str = "#d20f39"
SUCCESS_COLOR: str = "#40a02b"
WARNING_COLOR: str = "#df8e1d"
SUB_TEXT_COLOR: str = "#c6d0f5"

# Characters
DONE_ICON: str = "✔"
WARNING_ICON: str = "⚠"
ERROR_ICON: str = "✖"
INFO_ICON: str = ">"
CIRCLE_ICON: str = "○"
CIRCLE_FILLED_ICON: str = "●"
CHECK_ICON: str = "✓"

# Styles
HEADING_STYLE = RichStyle(color=HEADER_COLOR, bold=True)
SUB_HEADING_STYLE = RichStyle(color=PRIMARY_COLOR, bold=True)
TEXT_STYLE = RichStyle(bold=False, italic=False)
SUBTEXT_STYLE = RichStyle(bold=False, italic=False, color=SUB_TEXT_COLOR, dim=True)
ERROR_STYLE = RichStyle(bold=False, italic=True, color=ERROR_COLOR)
SUCCES_STYLE = RichStyle(bold=False, italic=False, color=SUCCESS_COLOR)
WARNING_STYLE = RichStyle(bold=False, italic=True, color=WARNING_COLOR)

CONSOLE = Console()


class _RichChoose:
    def __init__(
        self,
        options: List[str],
        prompt: str = "Choose options:",
        no_limit: bool = False,
    ):
        self.options = options
        self.prompt = prompt
        self.console = CONSOLE
        self.selected_indices: Set[int] = set()
        self.cursor_pos = 0
        self.no_limit = no_limit  # False = single selection, True = multiple selection

    def display(self):
        """Display the current state"""
        self.console.clear()

        # Prompt
        self.console.print(f"{self.prompt}\n", style=HEADING_STYLE)

        # Options
        for i, option in enumerate(self.options):
            prefix = INFO_ICON + " " if i == self.cursor_pos else "  "

            # Different symbols for single vs multiple selection
            if self.no_limit:
                checkbox = (
                    CHECK_ICON + " "
                    if i in self.selected_indices
                    else CIRCLE_ICON + " "
                )
            else:
                checkbox = (
                    CIRCLE_FILLED_ICON + " "
                    if i in self.selected_indices
                    else CIRCLE_ICON + " "
                )

            style = SUB_HEADING_STYLE if i in self.selected_indices else TEXT_STYLE

            if i == self.cursor_pos:
                style = f"bold reverse {style}"

            self.console.print(f"{prefix}[{style}]{checkbox}{option}[/{style}]")

        # Help text changes based on selection mode
        if self.no_limit:
            help_text = "↑/k: up • ↓/j: down • Space: toggle • Enter: confirm"
        else:
            help_text = "↑/k: up • ↓/j: down • Space: select • Enter: confirm"

        self.console.print(f"\n{help_text}", style=SUBTEXT_STYLE)

        # Show selection mode
        mode_text = "Multiple selection" if self.no_limit else "Single selection"
        self.console.print(f"Mode: {mode_text}", style=SUBTEXT_STYLE)

    def get_key(self):
        """Get a single key"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            # Handle escape sequences for arrow keys
            if key == "\x1b":
                key += sys.stdin.read(2)
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def handle_space(self):
        """Handle space key based on selection mode"""
        if self.no_limit:
            # Multiple selection: toggle
            if self.cursor_pos in self.selected_indices:
                self.selected_indices.remove(self.cursor_pos)
            else:
                self.selected_indices.add(self.cursor_pos)
        else:
            # Single selection: select only this one
            self.selected_indices.clear()
            self.selected_indices.add(self.cursor_pos)

    def run(self) -> List[str]:
        """Run the selection"""
        try:
            while True:
                self.display()
                key = self.get_key()

                if key == "\r" or key == "\n":  # Enter
                    break
                elif key == " ":  # Space
                    self.handle_space()
                elif key in ["k", "A"] or key == "\x1b[A":  # Up
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif key in ["j", "B"] or key == "\x1b[B":  # Down
                    self.cursor_pos = min(len(self.options) - 1, self.cursor_pos + 1)
                elif key.isdigit():  # Number selection
                    num = int(key) - 1
                    if 0 <= num < len(self.options):
                        self.cursor_pos = num
                        if not self.no_limit:
                            # In single selection mode, immediately select when using numbers
                            self.selected_indices.clear()
                            self.selected_indices.add(self.cursor_pos)

        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            return []
        finally:
            self.console.clear()

        selected_options = [self.options[i] for i in sorted(self.selected_indices)]

        return selected_options


class _RichConfirm:
    def __init__(self, prompt: str = "Confirm?", default_yes: bool = True):
        self.prompt = prompt
        self.default_yes = default_yes
        self.console = CONSOLE
        self.selected_yes = default_yes

    def display(self):
        """Display the confirmation dialog"""
        self.console.clear()

        # Build the prompt text
        prompt_text = RichText()
        prompt_text.append(self.prompt, style=HEADING_STYLE)
        prompt_text.append(" (y/N)" if not self.default_yes else " (Y/n)")

        # Center the prompt
        self.console.print(prompt_text)
        self.console.print()

        # Build the options line
        options_text = RichText()

        if self.selected_yes:
            options_text.append("• ", style=SUB_HEADING_STYLE)
            options_text.append("Yes", style=SUB_HEADING_STYLE)
            options_text.append("   ")
            options_text.append("  No", style=SUBTEXT_STYLE)
        else:
            options_text.append("  Yes", style=SUBTEXT_STYLE)
            options_text.append("   ")
            options_text.append("• ", style=SUB_HEADING_STYLE)
            options_text.append("No", style=SUB_HEADING_STYLE)

        # Center the options
        self.console.print(options_text)

        # Help text
        help_text = RichText()
        help_text.append("←/h: No • →/l: Yes • Enter: confirm", style=SUBTEXT_STYLE)
        self.console.print()
        self.console.print(help_text)

    def get_key(self):
        """Get a single key"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            # Handle escape sequences for arrow keys
            if key == "\x1b":
                key += sys.stdin.read(2)
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def run(self) -> bool:
        """Run the confirmation dialog"""
        try:
            while True:
                self.display()
                key = self.get_key()

                if key == "\r" or key == "\n":  # Enter
                    break
                elif key in ["y", "Y"]:  # Yes
                    self.selected_yes = False
                    break
                elif key in ["n", "N"]:  # No
                    self.selected_yes = True
                    break
                elif key in ["l", "C"] or key == "\x1b[C":  # Right arrow
                    self.selected_yes = False
                elif key in ["h", "D"] or key == "\x1b[D":  # Left arrow
                    self.selected_yes = True
                elif key == " ":  # Space toggles
                    self.selected_yes = not self.selected_yes

        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            return False
        finally:
            self.console.clear()

        return self.selected_yes


class Spinner:
    """
    Context manager for showing a live console spinner using `rich`.

    Args:
        message(str): Initial spinner message
    """

    def __init__(
        self,
        message: str,
    ):
        self.message = message
        self.spinner_style = "arc"
        self.spinner = RichSpinner(
            self.spinner_style, text=self._styled_text(message), style=TEXT_STYLE
        )
        self.live = RichLive(self.spinner, refresh_per_second=10)

    def _styled_text(self, text: str) -> RichText:
        return RichText(text, style=TEXT_STYLE)

    def update_text(self, new_message: str, log: bool = False) -> None:
        """Update the spinner text"""
        self.spinner.update(text=self._styled_text(new_message))

    def success(self, message: str, log: bool = False) -> None:
        """Show success message and stop spinner"""
        self.live.update(RichText(DONE_ICON + " " + message, style=SUCCES_STYLE))

    def error(self, message: str, log: bool = False) -> None:
        """Show error message and stop spinner"""
        self.live.update(RichText(ERROR_ICON + " " + message, style=ERROR_STYLE))

    def warning(self, message: str, log: bool = False) -> None:
        """Show warning message and stop spinner"""
        self.live.update(RichText(WARNING_ICON + " " + message, style=WARNING_STYLE))

    def __enter__(self):
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.live.stop()


def print_asci_title(text: str) -> None:
    styled_text = RichText(text=figlet_format(text), style=HEADING_STYLE)
    CONSOLE.print(styled_text)


def print_subtext(text: str) -> None:
    CONSOLE.print(RichText(text, style=SUBTEXT_STYLE))


def print_header(text: str) -> None:
    CONSOLE.print(text, style=HEADING_STYLE)


def print_info(text: str) -> None:
    CONSOLE.print(INFO_ICON + " " + text, style=TEXT_STYLE)


def print_success(text: str) -> None:
    CONSOLE.print(DONE_ICON + " " + text, style=SUCCES_STYLE)


def print_error(text: str) -> None:
    CONSOLE.print(ERROR_ICON + " " + text, style=ERROR_STYLE)


def print_warning(text: str) -> None:
    CONSOLE.print(WARNING_ICON + " " + text, style=WARNING_STYLE)


def print_newline(count: int = 1) -> None:
    CONSOLE.print("\n" * count, end="")


def choose_old(message: str, options: List[str]) -> str:
    """Display a message and present a list of options for the user to choose any one from."""
    CONSOLE.print(RichText(message, style=HEADING_STYLE))

    for i, option in enumerate(options, start=1):
        CONSOLE.print(f"{i}. {option}", style=TEXT_STYLE)

    choices = [str(i) for i in range(1, len(options) + 1)]
    selected = Prompt.ask("Choose an option (number)", choices=choices)
    return options[int(selected) - 1]


def checklist_old(items: List[str], title: str = "List") -> List[str]:
    """Display a checklist and allow the user to select multiple items."""
    CONSOLE.print(title, style=HEADING_STYLE)

    for i, item in enumerate(items, start=1):
        CONSOLE.print(f"{i}. {item}", style=TEXT_STYLE)

    selected_numbers = Prompt.ask(
        "Select items by their numbers separated by spaces (or 0 to skip)", default="0"
    )
    if selected_numbers.strip() == "0":
        return []

    selected_items = []
    for part in selected_numbers.split():
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(items):
                selected_items.append(items[idx])
    return selected_items


def confirm_old(title: str) -> bool:
    """Display a yes/no prompt."""
    CONSOLE.print(RichText(title, style=HEADING_STYLE))
    choice = Prompt.ask(choices=["y", "n"], default="y")
    return choice.lower() == "y"


def confirm(prompt: str = "Confirm?", default_yes: bool = False) -> bool:
    """Ask yes/No and returns True if yes, else False"""
    return _RichConfirm(prompt, default_yes).run()


def choose(
    *options, prompt: str = "Choose:", no_limit: bool = False
) -> Union[List[str], str, None]:
    """
    Choose one or multiple items from a list
    """
    if not options:
        return []

    if no_limit:
        chosen_list = _RichChoose(list(options), prompt, no_limit=True).run()
        return chosen_list if chosen_list else None

    chosen_list = _RichChoose(list(options), prompt, no_limit=False).run()
    return chosen_list[0] if chosen_list else None


def clear_console():
    """Reset console"""
    return CONSOLE.print("\033c", end="")


def clear_console_v():
    "Clear visible console"
    return CONSOLE.clear()


def get_console() -> Console:
    """Get console instance"""
    return CONSOLE
