import logging
from pathlib import Path
from typing import Optional
from .paths import SBDOTS_LOG_DIR


class Logger:
    def __init__(self, log_file: Optional[Path] = None):
        self.logfile = log_file or (SBDOTS_LOG_DIR / "base.log")
        self.logfile.parent.mkdir(parents=True, exist_ok=True)
        self.logfile.touch(exist_ok=True)

        logger_name = f"SBDots::{self.logfile.resolve()}"
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False  # Prevent logs from bubbling up

        # Clear existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        handler = logging.FileHandler(self.logfile, mode="a", encoding="utf-8")
        formatter = logging.Formatter("[%(asctime)s] - [%(levelname)s] - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

    def log_heading(self, title: str):
        separator = "=" * 50
        with open(self.logfile, "a", encoding="utf-8") as f:
            f.write(f"\n{separator}\n{title}\n{separator}\n")
