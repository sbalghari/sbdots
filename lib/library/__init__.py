import json

from .run_cmd import run_command
from .sys_ops import is_vm, is_laptop
from .fs_ops import path_lexists, copy, remove, create_symlink
from .pkg_ops import (
    is_installed,
    install_package,
    install_package_group,
    remove_package,
)
from .procs_ops import send_signal, find_pid_by_name, find_procs_by_name, kill_proc_tree
from .notification_utils import Notification, notiy_send
from .sudo_keep_alive import SudoKeepAlive
from utils.paths import SBDOTS_METADATA_FILE


__all__ = [
    "get_sbdots_version",
    "run_command",
    # System related operations
    "is_vm",
    "is_laptop",
    # FileSystem related operations
    "path_lexists",
    "copy",
    "remove",
    "create_symlink",
    # Processes related operations
    "send_signal",
    "find_pid_by_name",
    "find_procs_by_name",
    "kill_proc_tree",
    # Package related operations
    "is_installed",
    "install_package",
    "install_package_group",
    "remove_package",
    # Others
    "Notification",
    "notiy_send",
    "SudoKeepAlive",
]


def get_sbdots_version() -> str:
    """Get the current version of SBDots from metadata file."""
    try:
        with open(SBDOTS_METADATA_FILE, "r") as f:
            metadata = json.load(f)
            return metadata.get("version", "unknown")
    except Exception:
        return "unknown"
