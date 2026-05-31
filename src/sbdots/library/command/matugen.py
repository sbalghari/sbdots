from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Optional, Literal, Union

from ..config_utils import get_config, set_config
from sbdots.constants import MATUGEN_SECTION

# Type definitions for matugen options
ColorSchemeType = Literal[
    "scheme-content",
    "scheme-expressive",
    "scheme-fidelity",
    "scheme-fruit-salad",
    "scheme-monochrome",
    "scheme-neutral",
    "scheme-rainbow",
    "scheme-tonal-spot",
    "scheme-vibrant",
]

Mode = Literal["light", "dark"]
Prefer = Literal[
    "darkness",
    "lightness",
    "saturation",
    "less-saturation",
    "value",
    "closest-to-fallback",
]


class MatugenImage:
    """
    Wrapper for the 'matugen image' command
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the matugen wrapper

        Args:
            logger: Logger instance to use for logging
        """
        self.logger = logger or logging.getLogger(__name__)

    def _get_config_value(self, key: str) -> Optional[str]:
        """Get a configuration value from the settings file"""
        return get_config(key, section=MATUGEN_SECTION, logger=self.logger)

    def _set_config_value(self, key: str, value: str) -> bool:
        """Set a configuration value in the settings file"""
        return set_config(key, value, section=MATUGEN_SECTION, logger=self.logger)

    def _build_command(
        self, image_path: Union[str, Path], dry_run: bool = False
    ) -> list[str]:
        """
        Build the matugen command with current configuration

        Args:
            image_path: Path to the image file
            dry_run: If True, add --dry-run flag to the command

        Returns:
            List of command arguments
        """
        cmd = ["matugen", "image"]

        # Add image path
        cmd.append(str(image_path))

        # Get configuration values
        _source_color_index = self._get_config_value("source_color_index")
        _prefer = self._get_config_value("prefer")
        _fallback_color = self._get_config_value("fallback_color")
        _mode = self._get_config_value("mode")
        _scheme_type = self._get_config_value("type")

        # Set defaults if not in settings.ini
        source_color_index = "0" if _source_color_index is None else _source_color_index
        prefer = "closest-to-fallback" if _prefer is None else _prefer
        fallback_color = "#ca9ee6" if _fallback_color is None else _fallback_color
        mode = "light" if _mode is None else _mode
        scheme_type = "scheme-expressive" if _scheme_type is None else _scheme_type

        # Add options
        cmd.extend(["--source-color-index", source_color_index])
        cmd.extend(["--prefer", prefer])
        cmd.extend(["--fallback-color", fallback_color])
        cmd.extend(["-m", mode])
        cmd.extend(["-t", scheme_type])

        # Add dry-run flag if specified
        if dry_run:
            cmd.append("--dry-run")

        self.logger.debug(f"Built command: {' '.join(cmd)}")
        return cmd

    def execute(
        self,
        image_path: Union[str, Path],
        dry_run: bool = False,
        check: bool = True,
        capture_output: bool = False,
    ) -> subprocess.CompletedProcess:
        """
        Execute the matugen image command

        Args:
            image_path: Path to the image file
            dry_run: If True, add --dry-run flag (don't generate templates, reload apps, etc.)
            check: Whether to check return code (raises CalledProcessError on non-zero exit)
            capture_output: Whether to capture stdout/stderr

        Returns:
            CompletedProcess instance with command output

        Raises:
            FileNotFoundError: If matugen command is not found or image doesn't exist
            subprocess.CalledProcessError: If check=True and command returns non-zero exit code
        """
        image_path_obj = Path(image_path)

        # Validate image path
        if not image_path_obj.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        if not image_path_obj.is_file():
            raise ValueError(f"Path is not a file: {image_path}")

        cmd = self._build_command(image_path_obj, dry_run=dry_run)

        self.logger.info(f"Executing matugen command for image: {image_path}")
        self.logger.debug(f"Full command: {' '.join(cmd)}")

        try:
            if capture_output:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=check
                )
            else:
                result = subprocess.run(cmd, check=check)

            self.logger.info("Matugen command completed successfully")
            return result

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Matugen command failed with exit code {e.returncode}")
            if hasattr(e, "stderr") and e.stderr:
                self.logger.error(f"Stderr: {e.stderr}")
            raise
        except FileNotFoundError:
            self.logger.error(
                "matugen command not found. Please ensure matugen is installed and in PATH"
            )
            raise
