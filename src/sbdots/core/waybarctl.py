import logging
import typer
import signal

from sbdots.core.process import Process, start_proc
from sbdots.cli.ui.cli_utils import print_error, print_warning
from sbdots.utils.config_utils import get_config, set_config
from sbdots.utils.logger import setup_logging
from sbdots.utils.paths import USER_CONFIGS_DIR


class Waybar(Process):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        super().__init__("waybar", self.logger)

        # Define variables
        self.waybar_config_path = USER_CONFIGS_DIR / "waybar"
        self.default_style = "modern"
        self.current_style = self._get_style()
        self.current_style_path = self.waybar_config_path / self.current_style

        # Waybar config files
        self.config_file = self.current_style_path / "config.jsonc"
        self.css_file = self.current_style_path / "style.css"

    def _set_style(self, style) -> None:
        """Set the style under a 'Waybar' section in settings"""
        self.logger.debug(
            "Saving waybar's style in the settings...", extra={"style": style}
        )
        if not set_config("style", style, section="Waybar"):
            self.logger.error("Unable to save waybar style!")

        self.logger.info("Successfully saved waybar style setting.")

    def _get_style(self) -> str:
        """Load waybar style from settings, if none, set the default"""

        self.logger.debug("Loading waybar's current style from the settings...")
        _style = get_config("style", section="Waybar", logger=self.logger)

        if not _style:
            self.logger.debug(
                "Waybar style not found in the settings, saving with the default style"
            )
            self._set_style(self.default_style)
            return self.default_style

        self.logger.info(
            "Waybar style parsed from the settings", extra={"style": _style}
        )
        return _style

    def _validate_style(self) -> bool:
        """Check if the given config and css files exists or not."""
        self.logger.debug("Validating style files...")
        config_file = self.config_file.exists()
        css_file = self.css_file.exists()

        return config_file and css_file

    def _is_running(self) -> bool:
        return super().is_running()

    def start(self):
        if not self._validate_style():
            self.logger.error(
                "Style Validation failed, check '%s' and '%s' files exists.",
                self.config_file,
                self.css_file,
            )
            print_error(f"Invalid style: {self.current_style}")

        try:
            if self.is_running():
                print_warning("Waybar already running!")
                return

            result = start_proc(
                f"waybar -c {str(self.config_file)} -s {str(self.css_file)}",
                disown=True,
                background=False,
                dev_null_stderr=True,
                dev_null_stdout=True,
            )
            if not result:
                self.logger.error(
                    f"Unable to start waybar with style: {self.current_style}"
                )
            self.logger.info(f"Waybar started with style: {self.current_style}")
        except Exception as e:
            self.logger.exception("Unexpected error starting waybar:", exc_info=e)
            raise

    def reload(self):
        self.logger.debug("Restarting waybar...")
        return super().reload()

    def kill(self):
        self.logger.debug("Killing waybar...")
        if not self.is_running():
            print_error("Unable to kill, waybar not running!")
            return False

        return super().kill()

    def reload_config(self):
        self.logger.debug("Reloading waybar's configs...")
        if not self.is_running():
            print_error("Unable to reload config, waybar is not running!")
            return

        return super().send_signal(signal.SIGUSR2)

    def toggle(self):
        self.logger.debug("Toggling waybar's visibility...")
        if not self.is_running():
            print_error("Unable to toggle visibility, waybar is not running!")
            return

        return super().send_signal(signal.SIGUSR1)


def cli_api() -> typer.Typer:
    """Control waybar: reload, kill, start, etc."""
    cli = typer.Typer()
    waybar_inst = Waybar()

    common_option = typer.Option(False, "--verbose/--no-verbose", help="Verbose output")

    logger_initialized = False

    def _setup_logger(verbose: bool):
        nonlocal logger_initialized
        if logger_initialized:
            return

        setup_logging(
            __name__,
            verbose=verbose,
            use_rotating_file=False,
            file_handling_mode="w",
        )
        logger_initialized = True

    @cli.command()
    def start(verbose: bool = common_option):
        """Start waybar with custom config_file and css_file."""
        _setup_logger(verbose)
        waybar_inst.start()

    @cli.command()
    def kill(verbose: bool = common_option):
        "Kill waybar"
        _setup_logger(verbose)
        waybar_inst.kill()

    @cli.command()
    def toggle(verbose: bool = common_option):
        "Tell waybar to toggle it's visibility"
        _setup_logger(verbose)
        waybar_inst.toggle()

    @cli.command()
    def reload(verbose: bool = common_option):
        "Reload waybar by killing and restarting"
        _setup_logger(verbose)
        waybar_inst.reload()

    @cli.command()
    def reload_config(verbose: bool = common_option):
        "Tell waybar to reload it's config and style files"
        _setup_logger(verbose)
        waybar_inst.reload_config()

    return cli
