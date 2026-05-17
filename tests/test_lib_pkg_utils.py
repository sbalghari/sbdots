from unittest.mock import patch, MagicMock

from sbdots.library.pkg_utils import is_installed, install_package


class TestPkgUtils:
    """Tests for pkg_utils module"""

    @patch("sbdots.library.pkg_utils.run_command")
    def test_is_installed_returns_true_for_installed_package(
        self, mock_run_cmd
    ):
        """Test is_installed returns True when package is installed"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run_cmd.return_value = mock_result

        result = is_installed("vim")
        assert result is True

    @patch("sbdots.library.pkg_utils.run_command")
    def test_is_installed_returns_false_for_missing_package(
        self, mock_run_cmd
    ):
        """Test is_installed returns False when package is not installed"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run_cmd.return_value = mock_result

        result = is_installed("nonexistent_package")
        assert result is False

    @patch("sbdots.library.pkg_utils.is_installed")
    @patch("sbdots.library.pkg_utils.run_command")
    def test_install_package_skips_already_installed(
        self, mock_run_cmd, mock_is_inst
    ):
        """Test install_package skips installation if package is already installed"""
        mock_is_inst.return_value = True
        logger = MagicMock()

        result = install_package(logger, "vim")
        assert result is True
        assert not mock_run_cmd.called

    @patch("sbdots.library.pkg_utils.is_installed")
    @patch("sbdots.library.pkg_utils.run_command")
    def test_install_package_installs_missing_package(
        self, mock_run_cmd, mock_is_inst
    ):
        """Test install_package installs package if not installed"""
        mock_is_inst.return_value = False
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run_cmd.return_value = mock_result
        logger = MagicMock()

        result = install_package(logger, "vim")
        assert result is True
        assert mock_run_cmd.called

    @patch("sbdots.library.pkg_utils.is_installed")
    @patch("sbdots.library.pkg_utils.run_command")
    def test_install_package_handles_installation_failure(
        self, mock_run_cmd, mock_is_inst
    ):
        """Test install_package returns False on installation failure"""
        mock_is_inst.return_value = False
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run_cmd.return_value = mock_result
        logger = MagicMock()

        result = install_package(logger, "vim")
        assert result is False
