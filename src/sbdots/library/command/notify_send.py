from typing import Optional

from ..commands import run_command


def notify_send(
    summary: str,
    *,
    body: Optional[str] = None,
    urgency: str = "normal",
    expire_time: Optional[int] = None,
    icon: Optional[str] = None,
    app_name: Optional[str] = None,
    sync_tag: Optional[str] = None,
    progress_value: Optional[int] = None,
) -> None:
    """
    Wrapper for command 'notify-send' with progress and sync hints.
    """
    # Build command arguments
    args = ["notify-send"]

    # Add options
    if urgency in ["low", "normal", "critical"]:
        args.extend(["-u", urgency])
    else:
        raise ValueError(
            f"Invalid urgency: {urgency}. Must be 'low', 'normal', or 'critical'"
        )

    if expire_time is not None:
        args.extend(["-t", str(expire_time)])

    if icon:
        args.extend(["-i", icon])

    # Add sync_tag hint if provided
    if sync_tag:
        args.extend(["-h", f"string:x-canonical-private-synchronous:{sync_tag}"])

    # Add progress_value hint if provided
    if progress_value is not None:
        if not 0 <= progress_value <= 100:
            raise ValueError(
                f"Progress value must be between 0 and 100, got {progress_value}"
            )
        args.extend(["-h", f"int:value:{progress_value}"])

    if app_name:
        args.extend(["-a", app_name])

    # Add summary and body
    args.append(summary)
    if body:
        args.append(body)

    # Execute the command
    try:
        result = run_command(args, check=False)
        if result.returncode != 0:
            raise RuntimeError(
                f"notify-send exited with return code '{result.returncode}'"
            )
    except FileNotFoundError:
        raise RuntimeError("notify-send command not found. Is libnotify installed?")
    except Exception as e:
        raise RuntimeError(f"Failed to send notification: {e}")
