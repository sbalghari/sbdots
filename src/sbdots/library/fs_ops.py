from logging import Logger
from pathlib import Path
import shutil


def path_lexists(path: Path) -> bool:
    """Check for existing paths or broken symlinks."""
    return path.exists() or path.is_symlink()


def copy(src: Path, dest: Path, *, logger: Logger) -> bool:
    """
    Safely copy files or directories to destination.

    Behavior:
    - Files overwrite existing files
    - Directories merge recursively
    - Only conflicting paths/files are overitten
    """

    try:
        # Validate source exists
        if not src.exists():
            logger.error(f"Source path does not exist: {src}")
            return False

        # FILE COPY
        if src.is_file():
            # If destination is a directory,
            # copy file INTO directory
            target = dest / src.name if dest.is_dir() else dest

            target.parent.mkdir(parents=True, exist_ok=True)

            # Remove target only if its a file
            if target.exists() and not target.is_dir():
                logger.info(f"Destination file exists, removing: {target}")

                if not remove(target, logger=logger):
                    logger.error(f"Failed to remove destination: {target}")
                    return False

            if _copy(src, dest, logger=logger):
                return True

            logger.error(f"Failed copying file: {src} -> {target}")
            return False

        # DIRECTORY COPY
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)

            for item in src.iterdir():
                target = dest / item.name

                # Recursive merge copy
                if not copy(src=item, dest=target, logger=logger):
                    return False

            logger.info(f"Merged directory: {src} -> {dest}")
            return True

        logger.error(f"Unsupported path type: {src}")
        return False

    except Exception as e:
        logger.error(f"Unexpected error during copy: {src} -> {dest}: {e}")
        return False


def _copy(src: Path, dest: Path, *, logger: Logger) -> bool:
    try:
        if src.is_dir():
            # Merge directories safely
            shutil.copytree(
                src,
                dest,
                symlinks=True,
                dirs_exist_ok=True,
            )

        else:
            shutil.copy2(src, dest)

        logger.info(f"Copied successfully: {src} -> {dest}")
        return True

    except (PermissionError, OSError) as e:
        logger.warning(f"Permission denied copying: {src} -> {dest}: {e}")
        return False

    except Exception as e:
        logger.error(f"Error copying: {src} -> {dest}: {e}")
        return False


def remove(filepath: Path, *, logger: Logger) -> bool:
    """
    Remove a file, directory, or symlink safely.
    """

    filepath = Path(filepath)

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

    except (PermissionError, OSError) as e:
        logger.warning(f"Error removing path: {filepath}: {e}")
        return False

    except Exception as e:
        logger.error(f"Unexpected remove error: {filepath}: {e}")
        return False


def create_symlink(src: Path, trgt: Path, *, logger: Logger) -> bool:
    """Create or replace a symlink from source → target."""
    try:
        # Remove target if exists
        if not remove(logger=logger, filepath=trgt):
            logger.error(f"Failed to remove target: {trgt}")
            return False

        # Create symlink
        trgt.symlink_to(src, target_is_directory=src.is_dir())
        logger.info(f"Symlink created: {src} -> {trgt}")
        return True
    except Exception as e:
        logger.error(f"Error creating symlink: {src} -> {trgt}: {e}")
        return False
