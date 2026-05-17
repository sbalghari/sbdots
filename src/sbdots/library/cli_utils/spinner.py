from __future__ import annotations
from typing import Optional

from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner

from .console import CONSOLE
from ._base import panel, success, error, warning


class SpinnerProgress:
    """Context manager for showing a live console spinner."""

    def __init__(
        self, message: str, spinner_type: str = "dots", verbose: bool = False
    ):
        self.message = message
        self.spinner_type = spinner_type
        self.verbose = verbose

        self.spinner = Spinner(self.spinner_type, text=message, style="text")
        self.live = Live(
            panel("Processing", self.spinner),
            refresh_per_second=60,
            console=CONSOLE,
            transient=True,
        )

    def _styled_text(self, text: str) -> Text:
        return Text(text, style="text")

    def update_text(self, new_message: str) -> None:
        """Update the spinner text"""
        self.spinner.update(text=new_message, style="text")

    def success(self, message: str, details: Optional[str] = None) -> None:
        """Show success message in a panel"""
        if not self.verbose:
            self.live.update(success(message, details=details, use_panel=True))
        else:
            CONSOLE.print(success(message, details=details, use_panel=False))

    def error(self, message: str, details: Optional[str] = None) -> None:
        """Show error message in a panel"""
        if not self.verbose:
            self.live.update(error(message, details=details, use_panel=True))
        else:
            CONSOLE.print(error(message, details=details, use_panel=False))

    def warning(self, message: str, details: Optional[str] = None) -> None:
        """Show warning message in a panel"""
        if not self.verbose:
            self.live.update(warning(message, details=details, use_panel=True))
        else:
            CONSOLE.print(warning(message, details=details, use_panel=False))

    def __enter__(self):
        if not self.verbose:
            self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.verbose:
            self.live.stop()
