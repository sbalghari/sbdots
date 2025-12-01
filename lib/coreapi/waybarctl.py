import json
from pathlib import Path
import signal

from library import Process, start_proc
from utils.logger import Logger
from utils.paths import USER_CONFIGS_DIR, USER_SBDOTS_SETTINGS_DIR, SBDOTS_LOG_DIR


class Waybar(Process):
    def __init__(self) -> None:
        # Create logfile and setup logging
        self.logfile: Path = SBDOTS_LOG_DIR / "waybar.log"
        self.logfile.parent.mkdir(parents=True, exist_ok=True)
        self.logfile.unlink(missing_ok=True)
        self.logger = Logger(log_file=self.logfile) 

        super().__init__("waybar", self.logger)

        # Define variables
        self.waybar_config_path = USER_CONFIGS_DIR / "waybar"
        self.waybar_settings_file = USER_SBDOTS_SETTINGS_DIR / "waybar.json"
        self.default_style = "modern"
        self.current_style = self._load_settings()
        self.current_style_path = self.waybar_config_path / 'styles' / self.current_style

        # Waybar config files
        self.config_file = self.current_style_path / "config"
        self.css_file = self.current_style_path / "style.css"

    def _load_settings(self) -> str:
        """Load waybar style from settings file if exists, else create it and set the default_style"""
        try:
            with open(self.waybar_settings_file, "r", encoding="utf-8") as f:
                setting = json.load(f)
            return setting.get("style", self.default_style)
        except FileNotFoundError:
            self.logger.warning(
                f"'{self.waybar_settings_file}' not found, creating it..."
            )
            parent = self.waybar_settings_file.parent
            if not parent.exists:
                parent.mkdir(parents=True, exist_ok=True)

            with open(self.waybar_settings_file, "w", encoding="utf-8") as f:
                json.dump({"style": self.default_style}, f, indent=4)
            return self.default_style
        except Exception as e:
            self.logger.exception(
                "Unexpected error reading waybar settings file:", exc_info=e
            )
            raise

    def _validate_style(self) -> bool:
        """"Check if the given config and css files exists or not."""
        config_file = self.config_file.exists()
        css_file = self.css_file.exists()

        return config_file and css_file

    def _is_running(self) -> bool:
        return super().is_running()

    def start(self):
        """"Start waybar with custom config_file and css_file."""
        if not self._validate_style():
            self.logger.error(
                "Style Validation failed, check '%s' and '%s' files exists.",
                self.config_file,
                self.css_file,
            ) 
            print(f"Invalid style: {self.current_style}")
            return

        try:
            cmd = ["waybar", "-c", self.config_file, "-s", self.css_file]
            pid = start_proc(cmd)
            self.logger.info(
                "Waybar successfully started with style: '%s', pid: '%s'",
                self.current_style,
                pid,
            )
        except RuntimeError as e:
            self.logger.exception("Unexpected error starting waybar:", exc_info=e)

    def reload(self)
        "Reload waybar by killing and restarting"
        return super().reload()

    def kill(self):
        "Kill waybar"
        return super().kill()

    def reload_config(self):
        "Tell waybar to reload it's config and style files"
        return super().send_signal(signal.SIGUSR2)

    def toggle(self):
        "Tell waybar to toggle it's visibility"
        return super().send_signal(signal.SIGUSR1)


