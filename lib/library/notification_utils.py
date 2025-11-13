from pathlib import Path
from typing import Optional

from utils.paths import SBDOTS_NOTIFICATION_ICON
from utils.logger import Logger
from .run_cmd import run_command


class Notification:
    def __init__(
        self,
        title: str,
        body_text: str,
        urgency_level: str = "normal",
        expire_time: int = 5,
        icon_path: Path = SBDOTS_NOTIFICATION_ICON,
        progression: bool = False,
        logger: Optional[Logger] = None,
    ) -> None:
        self.logger = logger
        self.title = title
        self.body_text = body_text
        self.urgency_level = urgency_level
        self.expiry_time = expire_time * 1000  # Convert to ms
        self.icon_path = icon_path
        self.progression = progression
        self.progress_value: int = 0
        self._notification_id: int = 0
        self._context_active: bool = False

        self._validate_icon()
        self._validate_urgency_level()

    def _build_cmd(self) -> list[str]:
        cmd = [
            "notify-send",
            self.title,
            self.body_text,
            "-a",
            "SBDOTS",
            "-u",
            self.urgency_level,
            "-t",
            str(self.expiry_time),
            "-i",
            str(self.icon_path),
        ]
        if self.progression:
            cmd += ["-h", f"int:value:{self.progress_value}"]
        return cmd

    def _validate_icon(self) -> None:
        # Check for valid path type
        if not isinstance(self.icon_path, Path):
            self.icon_path = Path(self.icon_path)

        valid_path_extensions: tuple[str, ...] = (".png", ".svg", ".jpg")

        # Check for valid icon/image type
        if self.icon_path.suffix.lower() not in valid_path_extensions:
            if self.logger:
                self.logger.warning(
                    f"{self.icon_path} is not a valid icon/image path, falling back to default sbdots icon.."
                )
            self.icon_path = SBDOTS_NOTIFICATION_ICON
            return

        # Check if given icon exists
        if not self.icon_path.exists():
            if self.logger:
                self.logger.warning(
                    f"{self.icon_path} does not exists. falling back to default sbdots icon..."
                )
            self.icon_path = SBDOTS_NOTIFICATION_ICON

    def _validate_urgency_level(self) -> None:
        self.valid_urgency_levels: list[str] = ["normal", "low", "critical"]

        # Check for valid urgency levels
        if self.urgency_level not in self.valid_urgency_levels:
            if self.logger:
                self.logger.warning("Invalid urgency level given, setting to normal...")
            self.urgency_level = self.valid_urgency_levels[0]

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
        if self.logger:
            self.logger.warning(self.notification_id)

    def update(
        self,
        body_text: Optional[str] = None,
        progress_value: Optional[int] = None,
        urgency_level: Optional[str] = None,
        expiry_time: Optional[int] = None,
    ) -> None:
        if body_text:
            self.body_text = body_text
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


def notiy_send(message: str, title: str = "SBDots", urgency: str = "normal", time: int = 3) -> None:
    instance: Notification = Notification(
        title=title,
        body_text=message,
        urgency_level=urgency,
        expire_time=time
    )
    return instance.notify()