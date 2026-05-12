from __future__ import annotations

import logging
from configparser import ConfigParser
from typing import Optional

from sbdots.utils.logger import get_caller_logger
from sbdots.utils.paths import SBDOTS_CONFIG_DIR


SETTINGS_FILE = SBDOTS_CONFIG_DIR / "setting.ini"

DEFAULT_SECTION = "core"


def _ensure_paths() -> None:
    SBDOTS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.touch()


def _load_config() -> ConfigParser:
    _ensure_paths()
    cfg = ConfigParser()
    cfg.read(SETTINGS_FILE)
    return cfg


def _atomic_write(cfg: ConfigParser) -> None:
    tmp = SETTINGS_FILE.with_suffix(".tmp")
    with tmp.open("w") as f:
        cfg.write(f)
    tmp.replace(SETTINGS_FILE)


def get_config(
    key: str,
    *,
    section: str = DEFAULT_SECTION,
    logger: Optional[logging.Logger] = None,
) -> Optional[str]:
    """Get a setting value from the ini file"""

    logger = logger or get_caller_logger()

    if not key:
        logger.debug("Empty key passed to get_setting")
        return None

    cfg = _load_config()

    if not cfg.has_section(section):
        return None

    return cfg.get(section, key, fallback=None)


def set_config(
    key: str,
    value: str,
    *,
    section: str = DEFAULT_SECTION,
    overwrite: bool = True,
    logger: Optional[logging.Logger] = None,
) -> bool:
    """
    Set or update a setting.

    - Creates section if missing
    - Overwrites existing value by default
    """

    logger = logger or get_caller_logger()

    if not key or not value:
        logger.debug("Invalid key or value passed to set_setting")
        return False

    cfg = _load_config()

    if not cfg.has_section(section):
        cfg.add_section(section)

    if cfg.has_option(section, key) and not overwrite:
        logger.debug(
            "Key exists and overwrite disabled",
            extra={"section": section, "key": key},
        )
        return False

    cfg.set(section, key, value)
    _atomic_write(cfg)

    logger.info(
        "Setting saved",
        extra={"section": section, "key": key, "value": value},
    )
    return True


def remove_setting(
    key: str,
    *,
    section: str = DEFAULT_SECTION,
    logger: Optional[logging.Logger] = None,
) -> bool:
    """Remove a setting from the ini file"""

    logger = logger or get_caller_logger()

    if not key:
        logger.debug("Empty key passed to remove_setting")
        return False

    cfg = _load_config()

    if not cfg.has_section(section):
        return False

    if not cfg.has_option(section, key):
        return False

    cfg.remove_option(section, key)

    # Clean up empty sections
    if not cfg.items(section):
        cfg.remove_section(section)

    _atomic_write(cfg)

    logger.info(
        "Setting removed",
        extra={"section": section, "key": key},
    )
    return True
