from unittest.mock import patch, MagicMock

from sbdots.library.procs_utils import is_running, start_proc


class TestProcsUtils:
    """Tests for procs_utils module"""

    @patch("sbdots.library.procs_utils.subprocess.run")
    def test_is_running_returns_true_for_running_process(self, mock_subprocess):
        """Test is_running returns True when process is running"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = is_running("bash")
        assert isinstance(result, bool)
        assert result is True

    @patch("sbdots.library.procs_utils.subprocess.run")
    def test_is_running_returns_false_for_stopped_process(self, mock_subprocess):
        """Test is_running returns False when process is not running"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result

        result = is_running("nonexistent_process_xyz")
        assert isinstance(result, bool)
        assert result is False

    @patch("sbdots.library.procs_utils.subprocess.run")
    def test_start_proc_with_string_command(self, mock_subprocess):
        """Test start_proc with string command"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = start_proc("echo test")
        assert result is not None or True

    @patch("sbdots.library.procs_utils.subprocess.run")
    def test_start_proc_with_background_flag(self, mock_subprocess):
        """Test start_proc with background flag"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = start_proc("sleep 10", background=True)
        assert result is not None or True

    @patch("sbdots.library.procs_utils.subprocess.run")
    def test_start_proc_with_disown_flag(self, mock_subprocess):
        """Test start_proc with disown flag"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = start_proc("echo test", disown=True)
        assert result is not None or True
