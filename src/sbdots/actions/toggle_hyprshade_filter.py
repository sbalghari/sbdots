import logging
from subprocess import CompletedProcess

from sbdots.library.commands import run_command
from sbdots.library.notify import notiy_send
from sbdots.library.logger import setup_actions_state
from sbdots.library.config_utils import get_config, set_config


class ToggleHyprshadeFilter:
    def __init__(self, conn, *args) -> None:
        # Setup logging
        self.logger_name = self.__class__.__name__
        setup_actions_state(self.logger_name)
        self.logger = logging.getLogger(self.logger_name)

        # Socket connection
        self.conn = conn

        self.default_filter = "blue-light-filter"
        self.config_section = "Hyprshade"

    def _run_hyprshade_cmd(self, *args) -> CompletedProcess | None:
        """Runs a hyprshade command and return the CompletedProcess if success, else None"""
        try:
            return run_command(["hyprshade", *args])
        except FileNotFoundError:
            self.logger.error("Hyprshade not found on your system")
            return None
        except Exception as e:
            self.logger.exception("Unexpected error: ", exc_info=e)
            return None

    def _get_active_filter(self) -> str | None:
        result = self._run_hyprshade_cmd("current")
        if not result:
            return None
        out = (result.stdout or "").strip().lower()
        self.logger.debug(f"hyprshade current output: {out!r}")
        return out or None

    def _get_saved_filter(self) -> str | None:
        """Get the saved hyprshade filter from settings.
        If not found, save and return the default filter"""
        self.logger.debug("Loading hyprshade filter from settings...")
        _filter = get_config("filter", section=self.config_section, logger=self.logger)

        if not _filter:
            self.logger.debug(
                "Hyprshade filter not found in settings, saving with the default filter"
            )
            self._set_saved_filter(self.default_filter)
            return self.default_filter

        self.logger.info(
            "Hyprshade filter parsed from settings", extra={"filter": _filter}
        )
        return _filter

    def _set_saved_filter(self, filter_name: str) -> None:
        """Save the hyprshade filter to settings"""
        self.logger.debug(
            "Saving hyprshade filter to settings...", extra={"filter": filter_name}
        )
        if not set_config(
            "filter", filter_name, section=self.config_section, logger=self.logger
        ):
            self.logger.error("Unable to save hyprshade filter!")
            return

        self.logger.info("Successfully saved hyprshade filter setting.")

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
