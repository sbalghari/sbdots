from rich.prompt import Confirm, Prompt

from typing import Union

from .console import CONSOLE
from .output import print_subtext, print_error


def confirm(message: str = "Confirm?", default_yes: bool = False) -> bool:
    try:
        return Confirm.ask(
            message, console=CONSOLE, default=default_yes, show_default=True
        )

    except KeyboardInterrupt:
        print_subtext("Cancelled")
        return False


def prompt(
    message: str,
    password: bool = False,
) -> str:
    def _validator(input) -> bool:
        return len(input) > 0

    try:
        while True:
            input = Prompt.get_input(console=CONSOLE, prompt=message, password=password)

            if not _validator(input):
                print_error(
                    "Invalid! Input can not be empty.",
                    panel=False,
                )
                continue

            return input

    except KeyboardInterrupt:
        print_subtext("Cancelled")
        return ""


def chose(
    message: str,
    choices: list[str],
    skipable: bool = True,
    multiple: bool = False,
) -> Union[str, None, list[str]]:
    def _validator(input) -> bool:
        return len(input) > 0

    try:
        if multiple:
            return _chose_multiple(message, choices, skipable)

        while True:
            input = Prompt.ask(
                message, choices=choices, console=CONSOLE, case_sensitive=False
            )

            if not skipable:
                if _validator(input):
                    return input
                continue

        return input

    except KeyboardInterrupt:
        print_subtext("Cancelled")
        return None


def _chose_multiple(
    message: str,
    choices: list[str],
    skipable: bool = True,
) -> Union[list[str], None]:
    """numbered selection for multiple items."""
    try:
        CONSOLE.print(f"\n{message}", style="bold")
        for i, choice in enumerate(choices, 1):
            CONSOLE.print(f"{i:2d}. {choice}")

        while True:
            input_str = Prompt.ask(
                "\nSelect (numbers/ranges: 1 2 3 or 1-3)",
                console=CONSOLE,
            ).strip()

            if not input_str:
                if skipable:
                    return None
                print_error("Invalid! Input can not be empty.", panel=False)
                continue

            selected_indices = _parse_selection(input_str, len(choices))

            if selected_indices is None:
                print_error(
                    "Invalid selection! Please enter valid numbers or ranges.",
                    panel=False,
                )
                continue

            if not selected_indices and not skipable:
                print_error("Invalid! Please select at least one item.", panel=False)
                continue

            return [choices[i] for i in selected_indices] if selected_indices else None

    except KeyboardInterrupt:
        print_subtext("Cancelled")
        return None


def _parse_selection(input_str: str, total_items: int) -> Union[list[int], None]:
    """Parse selection input (e.g., '1 2 5-7' -> [0, 1, 4, 5, 6])."""
    selected = set()

    try:
        for part in input_str.replace(",", " ").split():
            if "-" in part:
                start, end = part.split("-")
                start, end = int(start.strip()), int(end.strip())
                if start < 1 or end > total_items or start > end:
                    return None
                selected.update(range(start - 1, end))
            else:
                num = int(part.strip())
                if num < 1 or num > total_items:
                    return None
                selected.add(num - 1)

        return sorted(list(selected))
    except (ValueError, AttributeError):
        return None
