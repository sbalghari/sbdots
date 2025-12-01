import json
from subprocess import CompletedProcess
from pathlib import Path

from library import run_command, notiy_send
from utils.paths import SBDOTS_LOG_DIR, USER_SBDOTS_SETTINGS_DIR
from utils.logger import Logger


class ToggleHyprshadeFilter:
    def __init__(self, conn, *args) -> None:
        # Create logfile and setup logging
        self.logfile: Path = SBDOTS_LOG_DIR / "hyprshade_filter.log"
        self.logfile.parent.mkdir(parents=True, exist_ok=True)
        self.logfile.unlink(missing_ok=True)
        self.logger = Logger(log_file=self.logfile)

        # Socket connection
        self.conn = conn

        self.default_filter = "blue-light-filter"
        self.filter_config_file = USER_SBDOTS_SETTINGS_DIR / "hyprshade_filter.json"

    def _run_hyprshade_cmd(self, *args) -> CompletedProcess | None:
        """Runs a hyprshade command and return the CompletedProcess if success, else None"""
        try:
            return run_command(["hyprshade", *args])
        except FileNotFoundError:
            self.logger.error("Hyprshade not found on your system")
            return None
        except Exception as e:
            self.logger.exception("Unexpected error: ", exec_info=e)
            return None

    def _get_active_filter(self) -> str | None:
        result = self._run_hyprshade_cmd("current")
        if not result:
            return None
        out = (result.stdout or "").strip().lower()
        self.logger.debug(f"hyprshade current output: {out!r}")
        return out or None

    def _get_saved_filter(self) -> str | None:
        """Get the saved hyprshade filter from the config file
        if config file doesn't exists, create with the default filter"""
        try:
            with open(self.filter_config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("filter")
        except FileNotFoundError:
            self.logger.warning(
                f"'{self.filter_config_file}' not found, creating it..."
            )
            parent = self.filter_config_file.parent
            if not self.filter_config_file.parent.exists():
                parent.mkdir(parents=True, exist_ok=True)
            with open(self.filter_config_file, "w", encoding="utf-8") as f:
                json.dump({"filter": self.default_filter}, f, indent=4)
            return self.default_filter
        except Exception as e:
            self.logger.exception("Unexpected error reading filter config", exc_info=e)
            return None

    def send(self, msg: str) -> None:
        try:
            self.conn.sendall(b"\n")
            self.conn.sendall((msg + "\n").encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def notify(self, msg) -> None:
        return notiy_send(msg, "SBDots - Actions")

    def main(self) -> None:
        filter2apply = self._get_saved_filter() or self.default_filter

        # If user explicitly set saved filter to "off", just try to turn hyprshade off.
        if filter2apply == "off":
            self.logger.debug(
                "Saved filter is 'off' — attempting to turn hyprshade off"
            )
            result = self._run_hyprshade_cmd("off")
            if not result:
                self.logger.error("Failed to run hyprshade off command")
                return
            if result.returncode != 0:
                self.logger.error(f"hyprshade off failed: {result.stderr}")
                return
            self.notify("hyprshade toggled off")
            self.logger.info("hyprshade toggled off")
            self.send("hyprshade: off")
            return

        # Otherwise saved filter is a name like "blue-light-filter"
        active = self._get_active_filter()
        # if active is None treat as not running
        if not active:
            self.logger.debug("Hyprshade not active, enabling filter: %s", filter2apply)
            result = self._run_hyprshade_cmd("on", filter2apply)
            if not result:
                self.logger.error("Failed to enable hyprshade")
                return
            if result.returncode != 0:
                self.logger.error(f"Failed to enable hyprshade: {result.stderr}")
                return
            self.notify(f"hyprshade enabled with {filter2apply}")
            self.logger.info(f"hyprshade enabled with {filter2apply}")
            self.send("hyprshade: on")
            return

        # If we get here, hyprshade is active. If the active filter equals saved filter, toggle off.
        # Otherwise change to the saved filter.
        if active == filter2apply.lower():
            self.logger.debug("Active filter matches saved filter — toggling off")
            result = self._run_hyprshade_cmd("off")
            if not result:
                self.logger.error("Failed to disable hyprshade")
                return
            if result.returncode != 0:
                self.logger.error(f"Failed to disable hyprshade: {result.stderr}")
                return
            self.notify("hyprshade toggled off")
            self.logger.info("hyprshade toggled off")
            print("hyprshade: off")
            return
        else:
            self.logger.debug(
                "Active filter differs from saved filter — switching to %s",
                filter2apply,
            )
            result = self._run_hyprshade_cmd("on", filter2apply)
            if not result:
                self.logger.error("Failed to switch hyprshade filter")
                return
            if result.returncode != 0:
                self.logger.error(f"Failed to enable hyprshade: {result.stderr}")
                return
            self.notify(f"hyprshade enabled with {filter2apply}")
            self.logger.info(f"hyprshade enabled with {filter2apply}")
            print("hyprshade: on")
            return
