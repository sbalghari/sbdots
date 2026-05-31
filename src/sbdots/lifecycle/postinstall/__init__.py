from logging import Logger

from sbdots.library.cli_utils import Spinner
from sbdots.constants import LifeCycleStep

from .apply_wallpaper import apply_wallpaper
from .start_service import start_services


class PostInstallHooks:
    """Manages the post-installation finalization steps."""

    def __init__(
        self,
        logger: Logger,
        dry_run: bool = False,
        verbose: bool = False,
    ):
        self.logger = logger
        self.dry_run = dry_run
        self.verbose = verbose
        self.failed_steps: list[str] = []

    def _get_hooks(self, spinner: Spinner) -> list[LifeCycleStep]:
        """
        Each step is a tuple of (description, function, is_critical).
        """
        return [
            (
                "Starting SBDots Services...",
                lambda: start_services(logger=self.logger, dry_run=self.dry_run),
                True,  # critical
            ),
            (
                "Applying wallpaper...",
                lambda: apply_wallpaper(logger=self.logger, dry_run=self.dry_run),
                False,  # Non-critical
            ),
        ]

    def run_hooks(self, spinner: Spinner) -> bool:
        """
        Execute all post-install hooks.

        Returns:
            bool: True if completed successfully, False if critical error occurred
        """
        self.logger.info("Executeing post-install hooks.")
        self.failed_steps = []

        hooks = self._get_hooks(spinner)
        all_success = True

        for step_text, step_func, is_critical in hooks:
            spinner.update_text(step_text)

            try:
                if not step_func():
                    if is_critical:
                        spinner.error(f"{step_text.strip()} failed.")
                        all_success = False
                        break
                    else:
                        spinner.warning(f"{step_text.strip()} completed with warnings.")
                        self.failed_steps.append(step_text.strip(" ."))
                else:
                    self.logger.info(f"{step_text.strip()} completed successfully.")

            except Exception as e:
                self.logger.error(f"Unexpected error during {step_text.strip()}: {e}")
                if is_critical:
                    spinner.error(f"{step_text.strip()} failed unexpectedly.")
                    all_success = False
                    break
                else:
                    spinner.warning(f"{step_text.strip()} completed with errors.")
                    self.failed_steps.append(step_text.strip(" ."))

        if all_success:
            spinner.success("All post-install hooks executed successfully")
        else:
            spinner.error("Error while executeing post-install hooks")

        return all_success
