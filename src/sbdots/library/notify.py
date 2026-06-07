from pathlib import Path
from typing import Optional

from .commands import run_command


class Notification:
    def __init__(
        self,
        text: str,
        *,
        title: str | None = None,
        urgency_level: str = "normal",
        expire_time: int = 5,
        icon_name: str | None = None,
        progress_value: int = 0,
        sync_tag: str | None = None,
    ):
        self.title = title
        self.text = text
        self.urgency_level = urgency_level
        self.expiry_time = expire_time * 1000  # Convert to ms
        self.progress_value: int = progress_value
        self.icon_name = icon_name
        self.sync_tag = sync_tag
        self._notification_id: int = 0
        self._context_active: bool = False
        self.notify_cmd: list[str] = []

        self._validate_urgency_level()

    def _build_cmd(self) -> list[str]:
        icon = self.icon_name if self.icon_name is not None else "sbdots"
        cmd = [
            "notify-send",
            "-a",
            "SBDOTS",
            "-u",
            self.urgency_level,
            "-t",
            str(self.expiry_time),
            "-i",
            icon,
        ]
        if self.progress_value:
            cmd += ["-h", f"int:value:{self.progress_value}"]

        if self.sync_tag:
            cmd += ["-h", f"string:x-canonical-private-synchronous:{self.sync_tag}"]

        if self.title:
            cmd += self.title

        cmd += self.text
        return cmd

    def is_file_path(self, s: str) -> bool:
        # check if it contains common path separators or file extensions
        if any(x in s for x in ("/", "\\")) or "." in Path(s).name:
            return True
        return False

    def _validate_urgency_level(self) -> None:
        self.valid_urgency_levels: list[str] = ["normal", "low", "critical"]

        # Check for valid urgency levels
        if self.urgency_level not in self.valid_urgency_levels:
            raise ValueError

    def notify(self) -> None:
        self.notify_cmd = self._build_cmd()

        if not self._context_active:
            run_command(self.notify_cmd)
        else:
            print("Dont use notify(), use update() instead")

    def _notify_n_catch_id(self) -> None:
        self.notify_cmd.append("-p")
        result = run_command(self.notify_cmd)
        self.notification_id = result.stdout.strip()

    def update(
        self,
        text: Optional[str] = None,
        progress_value: Optional[int] = None,
        urgency_level: Optional[str] = None,
        expiry_time: Optional[int] = None,
    ) -> None:
        if text:
            self.text = text
        if progress_value:
            self.progress_value = progress_value
        if urgency_level:
            self.urgency_level = urgency_level
        if expiry_time:
            self.expiry_time = expiry_time * 1000

        # Update the the existing notification
        self.notify_cmd = self._build_cmd()
        self.notify_cmd.append("-r")
        self.notify_cmd.append(self.notification_id)
        run_command(self.notify_cmd)

    def __enter__(self):
        self.progression = True
        self._context_active = True
        # idk why but swaync ignores the <-t 0> <-h boolean:resident:false> so forced to this,
        self.expiry_time = 10000
        self.notify_cmd = self._build_cmd()
        self._notify_n_catch_id()
        return self

    def __exit__(self, *args) -> None:
        self.update(progress_value=100, expiry_time=1)
        self._context_active = False
