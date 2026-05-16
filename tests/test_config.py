import pytest
from pathlib import Path

from sbdots.library.config_utils import (
    read_rich_theme,
)

from sbdots.utils.exceptions import ConfigNotFound


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------


def write_toml(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------
# read_config
# ---------------------------------------------------------------------


def test_read_config_success(tmp_path: Path):
    config_file = tmp_path / "config.toml"

    write_toml(
        config_file,
        """
        [env]
        name = "prod"

        [service]
        title = "{env.name}"
        """,
    )

    cfg = read_rich_theme(config_file)

    assert cfg["env"]["name"] == "prod"
    assert cfg["service"]["title"] == "prod"


def test_read_config_preserves_types(tmp_path: Path):
    config_file = tmp_path / "config.toml"

    write_toml(
        config_file,
        """
        [env]
        port = 8080

        [server]
        port = "{env.port}"
        """,
    )

    cfg = read_rich_theme(config_file)

    assert cfg["server"]["port"] == 8080
    assert isinstance(cfg["server"]["port"], int)


def test_read_config_file_not_found(tmp_path: Path):
    missing = tmp_path / "missing.toml"

    with pytest.raises(ConfigNotFound, match="Config file"):
        read_rich_theme(missing)


# ---------------------------------------------------------------------
# read_rich_theme
# ---------------------------------------------------------------------


def test_read_rich_theme_flattens(tmp_path: Path):
    theme_file = tmp_path / "theme.toml"

    write_toml(
        theme_file,
        """
        [colors]
        primary = "blue"

        [colors.background]
        main = "#000"
        alt = "#111"
        """,
    )

    theme = read_rich_theme(theme_file)

    assert theme == {
        "colors": {
            "primary": "blue",
            "background.main": "#000",
            "background.alt": "#111",
        }
    }


def test_read_rich_theme_with_resolution(tmp_path: Path):
    theme_file = tmp_path / "theme.toml"

    write_toml(
        theme_file,
        """
        [base]
        fg = "white"

        [colors]
        text = "{base.fg}"
        """,
    )

    theme = read_rich_theme(theme_file)

    assert theme == {
        "base": {
            "fg": "white",
        },
        "colors": {
            "text": "white",
        },
    }
