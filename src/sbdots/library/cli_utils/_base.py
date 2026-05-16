from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

from rich.text import Text
from rich.box import ROUNDED
from rich.panel import Panel

if TYPE_CHECKING:
    from rich.console import RenderableType

from .console import ICONS


def panel(
    title: str, content: RenderableType, style: str = "border.primary", *args
) -> Panel:
    return Panel(
        content,
        ROUNDED,
        *args,
        title=title,
        title_align="left",
        border_style=style,
        style="text",
        width=60,
    )


def _build_content(message: str, details: Optional[str], style: str) -> Text:
    content = Text(message, style=style)
    if details:
        content.append("\n")
        content.append(Text(details, style="subtext"))

    return content


def _output(
    *,
    message: str,
    details: Optional[str],
    text_style: str,
    title: str,
    border_style: str,
    use_panel: bool,
) -> Union[Panel, Text]:
    content = _build_content(message, details, text_style)

    if not use_panel:
        return content

    return panel(title, content, style=border_style)


def info(
    message: str, *, details: Optional[str] = None, use_panel: bool = True
):
    return _output(
        message=message,
        details=details,
        text_style="text",
        title=f"{ICONS['info']} Info",
        border_style="border.info",
        use_panel=use_panel,
    )


def success(
    message: str, *, details: Optional[str] = None, use_panel: bool = True
):
    return _output(
        message=message,
        details=details,
        text_style="success",
        title=f"{ICONS['done']} Success!",
        border_style="border.success",
        use_panel=use_panel,
    )


def error(
    message: str, *, details: Optional[str] = None, use_panel: bool = True
):
    return _output(
        message=message,
        details=details,
        text_style="error",
        title=f"{ICONS['error']} Error!",
        border_style="border.error",
        use_panel=use_panel,
    )


def warning(
    message: str, *, details: Optional[str] = None, use_panel: bool = True
):
    return _output(
        message=message,
        details=details,
        text_style="warning",
        title=f"{ICONS['warning']} Warning!",
        border_style="border.warning",
        use_panel=use_panel,
    )
