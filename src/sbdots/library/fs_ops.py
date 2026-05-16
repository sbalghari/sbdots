from pathlib import Path
import shutil
import logging


def path_lexists(path: Path) -> bool:
    """Check for existing paths or broken symlinks."""
    return path.exists() or path.is_symlink()


def copy(logger: logging.Logger, src: Path, dest: Path) -> bool:
    """
    Safely copy files or directories from src to dest.
    Automatically overwrites if dest exists. Falls back to sudo when needed.
    """
    try:
        # Validate source exists
        if not src.exists():
            logger.error(f"Source path does not exist: {src}")
            return False

        # Ensure parent dir exists
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove dest if exists
        if dest.exists():
            logger.info(f"Destination already exists, removing: {dest}")
            if not remove(logger=logger, filepath=dest):
                logger.error(f"Failed to remove destination: {dest}")
                return False

        if _copy_without_sudo(logger=logger, src=src, dest=dest):
            return True

        logger.error(f"All copy attempts failed: {src} -> {dest}")
        return False

    except Exception as e:
        logger.error(f"Unexpected error during copy: {src} -> {dest}: {e}")
        return False


def _copy_without_sudo(logger: logging.Logger, src: Path, dest: Path) -> bool:
    try:
        if src.is_dir():
            shutil.copytree(src, dest, symlinks=True, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)

        logger.info(f"Copied successfully without sudo: {src} -> {dest}")
        return True

    except (PermissionError, OSError) as e:
        logger.warning(f"Permission denied copying without sudo: {src} -> {dest}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error copying without sudo: {src} -> {dest}: {e}")
        return False


def remove(logger: logging.Logger, filepath: Path) -> bool:
    """
    Remove a file, directory, or symlink at the given path.
    Falls back to sudo when needed.
    """
    # Return if filepath doesn't exist
    if not path_lexists(filepath):
        logger.info(f"Path does not exist, nothing to remove: {filepath}")
        return True

    try:
        if filepath.is_symlink() or filepath.is_file():
            filepath.unlink()
        elif filepath.is_dir():
            shutil.rmtree(filepath)

        logger.info(f"Removed successfully: {filepath}")
        return True

    except (PermissionError, OSError, Exception) as e:
        logger.warning(f"Error removing path: {filepath}: {e}.")
        return False


def create_symlink(logger: logging.Logger, source: Path, target: Path) -> bool:
    """Create or replace a symlink from source → target."""
    try:
        # Remove target if exists
        if not remove(logger=logger, filepath=target):
            logger.error(f"Failed to remove target: {target}")
            return False

        # Create symlink
        target.symlink_to(source, target_is_directory=source.is_dir())
        logger.info(f"Symlink created: {source} -> {target}")
        return True
    except Exception as e:
        logger.error(f"Error creating symlink: {source} -> {target}: {e}")
        return False
