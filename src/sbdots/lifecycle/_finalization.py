import logging

from sbdots.library.cli_utils import Spinner
from sbdots.constants import FinalizationStep

from .postinstall import (
    apply_gtk_theme,
    apply_wallpaper,
    reload_hyprland,
    start_services,
)


class FinalizationManager:
    """Manages the post-installation finalization steps."""

    def __init__(
        self,
        logger: logging.Logger,
        dry_run: bool = False,
        verbose: bool = False,
    ):
        self.logger = logger
        self.dry_run = dry_run
        self.verbose = verbose
        self.failed_steps: list[str] = []

    def _get_finalization_steps(
        self, spinner: Spinner
    ) -> list[FinalizationStep]:
        """
        Returns a list of finalization steps.

        Each step is a tuple of (description, function, is_critical).
        """
        return [
            (
                "Starting SBDots Services...",
                lambda: start_services(
                    logger=self.logger, dry_run=self.dry_run
                ),
                True,  # critical
            ),
            (
                "Reloading Hyprland...",
                lambda: reload_hyprland(dry_run=self.dry_run),
                False,  # Non-critical
            ),
            (
                "Installing GTK Catppuccin theme...",
                lambda: apply_gtk_theme(
                    spinner=spinner, logger=self.logger, dry_run=self.dry_run
                ),
                True,  # Critical
            ),
            (
                "Applying wallpaper...",
                lambda: apply_wallpaper(
                    logger=self.logger, dry_run=self.dry_run
                ),
                False,  # Non-critical
            ),
        ]

    def finalize(self, spinner: Spinner) -> bool:
        """
        Execute all finalization steps.

        Returns:
            bool: True if finalization completed successfully, False if critical error occurred
        """
        self.logger.info("Starting finalization phase")
        self.failed_steps = []

        finalization_steps = self._get_finalization_steps(spinner)
        all_success = True

        for step_text, step_func, is_critical in finalization_steps:
            spinner.update_text(step_text)

            try:
                if not step_func():
                    if is_critical:
                        spinner.error(f"{step_text.strip()} failed.")
                        all_success = False
                        break
                    else:
                        spinner.warning(
                            f"{step_text.strip()} completed with warnings."
                        )
                        self.failed_steps.append(step_text.strip(" ."))
                else:
                    self.logger.info(
                        f"{step_text.strip()} completed successfully."
                    )

            except Exception as e:
                self.logger.error(
                    f"Unexpected error during {step_text.strip()}: {e}"
                )
                if is_critical:
                    spinner.error(f"{step_text.strip()} failed unexpectedly.")
                    all_success = False
                    break
                else:
                    spinner.warning(
                        f"{step_text.strip()} completed with errors."
                    )
                    self.failed_steps.append(step_text.strip(" ."))

        if all_success:
            spinner.success("Finalization completed successfully.")
        else:
            spinner.error("Finalization failed.")

        return all_success
