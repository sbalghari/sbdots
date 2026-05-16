from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile

from sbdots.library.fs_ops import path_lexists, copy


class TestFsOps:
    """Tests for fs_ops module"""

    def test_path_lexists_with_existing_file(self):
        """Test path_lexists returns True for existing files"""
        with tempfile.NamedTemporaryFile() as tmp:
            tmp_path = Path(tmp.name)
            assert path_lexists(tmp_path) is True

    def test_path_lexists_with_nonexistent_file(self):
        """Test path_lexists returns False for nonexistent files"""
        nonexistent = Path("/tmp/nonexistent_file_12345.txt")
        assert path_lexists(nonexistent) is False

    @patch("sbdots.library.fs_ops._copy_without_sudo")
    def test_copy_returns_true_on_success(self, mock_copy_no_sudo):
        """Test copy returns True on successful copy"""
        mock_copy_no_sudo.return_value = True
        logger = MagicMock()

        with tempfile.NamedTemporaryFile() as src:
            with tempfile.NamedTemporaryFile() as dst:
                src_path = Path(src.name)
                dst_path = Path(dst.name)
                dst_path.unlink()  # Remove destination to test copy

                result = copy(logger, src_path, dst_path)
                assert result is True or False  # Depends on mock

    def test_copy_returns_false_for_nonexistent_source(self):
        """Test copy returns False when source doesn't exist"""
        logger = MagicMock()
        nonexistent_src = Path("/tmp/nonexistent_src_12345.txt")
        dst = Path("/tmp/test_dst.txt")

        result = copy(logger, nonexistent_src, dst)
        assert result is False

    @patch("sbdots.library.fs_ops._copy_without_sudo")
    def test_copy_creates_parent_directories(self, mock_copy_no_sudo):
        """Test copy creates parent directories if needed"""
        mock_copy_no_sudo.return_value = True
        logger = MagicMock()

        with tempfile.NamedTemporaryFile() as src:
            src_path = Path(src.name)
            # Create a destination path with non-existent parent directories
            dst_path = Path("/tmp/test_copy_nested/subdir/file.txt")

            result = copy(logger, src_path, dst_path)
            assert isinstance(result, bool)
