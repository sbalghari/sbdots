from typing import Callable
from logging import Logger

from sbdots.constants import LifeCycleStep
from .dotfiles import DotfilesInstaller
from .packages import OptPackagesInstaller
from .wallpapers import WallpapersInstaller
from .auto_power_saver import AutoPowerSaverInstaller

from time import sleep  # temp


class ComponentsManager:
    """Manages sbdots's components, i.e: their installation, uninstallaion and etc"""

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

    def _get_components(self) -> list[LifeCycleStep]:
        """
        Each step is a tuple of (description, function, is_critical).
        """
        return [
            (
                "Dotfiles",
                lambda: DotfilesInstaller(
                    dry_run=self.dry_run, logger=self.logger, verbose=self.verbose
                ).install(),
                True,
            ),
            (
                "Wallpapers",
                lambda: WallpapersInstaller(
                    dry_run=self.dry_run, logger=self.logger, verbose=self.verbose
                ).install(),
                True,
            ),
            (
                "Recommended Packages",
                lambda: OptPackagesInstaller(
                    dry_run=self.dry_run, logger=self.logger, verbose=self.verbose
                ).install(),
                False,
            ),
            (
                "Auto Power Saver",
                lambda: AutoPowerSaverInstaller().install(
                    logger=self.logger,
                    dry_run=self.dry_run,
                    verbose=self.verbose,
                ),
                False,
            ),
        ]

    def install(self, sep_console_func: Callable) -> bool:
        self.logger.info("Starting installation of main components...")

        components = self._get_components()
        success = True

        for component_name, install_func, is_critical in components:
            self.logger.info(f"Installing {component_name}...")
            sleep(1)

            try:
                if sep_console_func(lambda: install_func()):
                    self.logger.info(f"{component_name} installed successfully.")
                else:
                    self.logger.error(f"{component_name} installation failed.")
                    self.failed_steps.append(component_name)
                    if is_critical:
                        success = False
                        break
                    else:
                        self.failed_steps.append(component_name)

            except Exception as e:
                self.logger.error(f"Unexpected error installing {component_name}: {e}")
                self.failed_steps.append(component_name)
                success = False

        return success
