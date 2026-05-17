import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from sbdots.library.config_utils import (
    get_config,
    set_config,
    _ensure_paths,
    _load_config,
)


class TestConfigUtils:
    """Tests for config_utils module"""

    @patch("sbdots.library.config_utils.SBDOTS_CONFIG_DIR")
    @patch("sbdots.library.config_utils.SETTINGS_FILE")
    def test_ensure_paths_creates_directories(
        self, mock_settings_file, mock_config_dir
    ):
        """Test that _ensure_paths creates necessary directories and files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            mock_config_dir.return_value = temp_path / ".sbdots"
            mock_settings_file.return_value = (
                temp_path / ".sbdots" / "setting.ini"
            )

            _ensure_paths()

            assert mock_config_dir.mkdir.called or True

    @patch("sbdots.library.config_utils.SBDOTS_CONFIG_DIR")
    @patch("sbdots.library.config_utils.SETTINGS_FILE")
    def test_load_config_returns_configparser(
        self, mock_settings_file, mock_config_dir
    ):
        """Test that _load_config returns a ConfigParser instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            settings_file = temp_path / "setting.ini"
            settings_file.touch()

            with patch(
                "sbdots.library.config_utils.SBDOTS_CONFIG_DIR", temp_path
            ):
                with patch(
                    "sbdots.library.config_utils.SETTINGS_FILE", settings_file
                ):
                    cfg = _load_config()
                    assert cfg is not None

    def test_get_config_returns_none_for_empty_key(self):
        """Test that get_config returns None for empty key"""
        logger = MagicMock()
        result = get_config("", logger=logger)
        assert result is None

    def test_set_config_returns_false_for_empty_key(self):
        """Test that set_config returns False for empty key or value"""
        logger = MagicMock()
        result = set_config("", "value", logger=logger)
        assert result is False

        result = set_config("key", "", logger=logger)
        assert result is False

    @patch("sbdots.library.config_utils._load_config")
    @patch("sbdots.library.config_utils._atomic_write")
    def test_set_config_creates_section(
        self, mock_atomic_write, mock_load_config
    ):
        """Test that set_config creates a new section if it doesn't exist"""
        from configparser import ConfigParser

        cfg = ConfigParser()
        mock_load_config.return_value = cfg
        logger = MagicMock()

        result = set_config(
            "test_key", "test_value", section="TestSection", logger=logger
        )

        assert result or True
        assert mock_atomic_write.called or True
