import json

from utils.paths import SBDOTS_METADATA_FILE


def get_sbdots_version() -> str:
    """Get the current version of SBDots from metadata file."""
    try:
        with open(SBDOTS_METADATA_FILE, "r") as f:
            metadata = json.load(f)
            return metadata.get("version", "unknown")
    except Exception:
        return "unknown"
