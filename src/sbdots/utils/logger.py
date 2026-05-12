from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union
from enum import Enum
import sys
import os

from rich.logging import RichHandler


SBDOTS_STATE_DIR = Path(
    os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")
) / "sbdots"

SBDOTS_LOG_DIR = SBDOTS_STATE_DIR / "logs"


class LogLevel(Enum):
    """Log levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# internal state
_GLOBAL_SETUP = {}


def _file_fmt() -> logging.Formatter:
    return logging.Formatter(
        "[%(asctime)s] - [%(name)s] - [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _get_handlers(
    console: bool = True,
    rotating_file: bool = False,
    file: bool = False,
    sys_stream: bool = False,
    file_path: Union[str, Path, None] = None,
    file_handling_mode: str = "a",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> list:
    """Build a list of handlers based on the options provided"""
    handlers = []

    if file or rotating_file:
        if not file_path:
            raise ValueError(
                "A file path is needed to get 'file' and 'rotating_file' handlers!"
            )

    if not isinstance(file_path, str):
        file_path = str(file_path)

    if console:
        ch = RichHandler(
            rich_tracebacks=True,
            show_time=True,
            omit_repeated_times=False,
            show_level=True,
            show_path=True,
            markup=True,
        )
        ch.setFormatter(logging.Formatter("- %(message)s"))
        ch.setLevel(LogLevel.INFO.value)
        handlers.append(ch)

    if rotating_file:
        rfh = RotatingFileHandler(
            filename=file_path,
            mode=file_handling_mode,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        rfh.setLevel(LogLevel.DEBUG.value)
        rfh.setFormatter(_file_fmt())
        handlers.append(rfh)

    if file:
        fh = logging.FileHandler(
            filename=file_path,
            mode=file_handling_mode,
            encoding="utf-8",
        )
        fh.setLevel(LogLevel.DEBUG.value)
        fh.setFormatter(_file_fmt())
        handlers.append(fh)

    if sys_stream:
        sh = logging.StreamHandler(sys.stdout)
        handlers.append(sh)

    return handlers


def setup_logging(
    name: str,
    *,
    verbose: bool = False,
    use_rotating_file: bool = True,
    file_handling_mode: str = "a",
    log_dir: Optional[Path] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure logging for cli: sbdotsctl, sbdots, etc.
    Defaults: console if verbose else rotating file
    """
    if name in _GLOBAL_SETUP:
        return  # already configured

    if log_dir is None:
        log_dir = SBDOTS_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    if log_file is None:
        log_file = f"{name}.log"

    file_path = log_dir / log_file

    # Create top-level logger for this name
    root_logger = logging.getLogger(name)
    root_logger.setLevel(LogLevel.DEBUG.value)

    # Add handlers
    handlers = _get_handlers(
        console=verbose,
        rotating_file=use_rotating_file,
        file=(not use_rotating_file),
        file_path=file_path,
        file_handling_mode=file_handling_mode,
    )
    for h in handlers:
        root_logger.addHandler(h)
    root_logger.propagate = False

    _GLOBAL_SETUP[name] = {
        "log_dir": str(log_dir),
        "log_file": str(log_file),
        "handlers": handlers,
    }


def setup_daemon_logging(
    name: str,
    *,
    log_dir: Optional[Path] = None,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    """
    Configure logging for a SBDots-Daemon scripts.
    Default: sys.stdout stream and rotating file append.
    """
    if log_dir is None:
        log_dir = SBDOTS_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    if log_file is None:
        log_file = f"{name}.log"

    file_path = log_dir / log_file

    handlers = _get_handlers(
        console=False,
        rotating_file=True,
        file_handling_mode="a",
        file_path=file_path,
        max_bytes=max_bytes,
        backup_count=backup_count,
    )

    logger = logging.getLogger(name)
    logger.setLevel(LogLevel.DEBUG.value)
    for h in handlers:
        logger.addHandler(h)
    logger.propagate = False

    _GLOBAL_SETUP[name] = {
        "log_dir": str(log_dir),
        "log_file": str(log_dir / log_file),
        "handlers": handlers,
    }


def setup_actions_state(name: str, log_level=LogLevel.DEBUG.value) ->None:
    """
    Configure logging for SBDots-Actions to save as states.
    """
    # Ensure state dir exists
    state_dir = SBDOTS_STATE_DIR
    state_dir.mkdir(parents=True, exist_ok=True)

    log_file = f"{name}.state.log"

    file_path = state_dir / log_file

    handlers = _get_handlers(
        console=False,
        file=True,
        file_handling_mode="w",
        file_path=file_path,
    )

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(handlers[0])
    logger.propagate = False

    _GLOBAL_SETUP[name] = {
        "log_dir": str(state_dir),
        "log_file": str(state_dir / log_file),
        "handlers": handlers,
    }

def get_caller_logger(default: str = "sbdots") -> logging.Logger:
    """
    Fallback for library functions when caller didn't pass a logger.
    """
    return logging.getLogger(default)
