from pathlib import Path
from typing import List, Any
import subprocess


def run_command(command: List[Any]) -> subprocess.CompletedProcess:
    """Run a command safely and return its result."""
    if not command:
        raise ValueError("Command must be a non-empty list of strings.")

    # Convert Path objects to strings
    str_command = [str(arg) if isinstance(arg, Path) else arg for arg in command]

    try:
        return subprocess.run(str_command, text=True, capture_output=True)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Executable not found: {command[0]}") from e
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Subprocess error: {' '.join(str_command)}\n{e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {' '.join(str_command)}\n{e}") from e
