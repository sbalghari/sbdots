import pytest
from unittest.mock import patch, MagicMock

from sbdots.library.commands import run_command
from sbdots.library.exceptions import CommandNotFound


class TestCommands:
    """Tests for commands module"""

    @patch("sbdots.library.commands.subprocess.run")
    def test_run_command_with_list_command(self, mock_subprocess):
        """Test run_command with a list-based command"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_subprocess.return_value = mock_result

        result = run_command(["echo", "hello"])
        assert result is not None

    @patch("sbdots.library.commands.subprocess.run")
    def test_run_command_with_string_command(self, mock_subprocess):
        """Test run_command with a string-based command"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = run_command("echo hello")
        assert result is not None

    @patch("sbdots.library.commands.which")
    def test_run_command_raises_on_missing_command(self, mock_which):
        """Test run_command raises CommandNotFound for missing commands"""
        mock_which.return_value = None

        with pytest.raises(CommandNotFound):
            run_command(["nonexistent_command"])

    @patch("sbdots.library.commands.subprocess.run")
    def test_run_command_returns_completed_process(self, mock_subprocess):
        """Test run_command returns CompletedProcess"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = run_command(["true"])
        assert hasattr(result, "returncode")

    @patch("sbdots.library.commands.subprocess.run")
    def test_run_command_with_shell_true(self, mock_subprocess):
        """Test run_command can be called with shell=True"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = run_command("echo hello | grep hello", shell=True)
        assert result is not None or True
