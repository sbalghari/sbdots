class ProcessError(Exception):
    """Custom exception for process-related errors"""

    pass


class ProcessNotKilled(ProcessError):
    """Raised when psutil is not successful at killing a process"""

    def __init__(self, pid, reason=None):
        self.pid = pid
        self.reason = reason
        msg = f"Failed to kill process {pid}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class CommandNotFound(FileNotFoundError):
    def __init__(
        self, command, stderr=None, stdout=None, return_code=None
    ) -> None:
        self.command = command
        self.stderr = stderr
        self.stdout = stdout
        self.return_code = return_code
        msg = f"The command {self.command} not found"

        if self.stdout:
            msg += f", stdout: [{self.stdout}]"
        if self.stderr:
            msg += f", stderr: [{self.stderr}]"
        if self.return_code:
            msg += f", return code: [{self.return_code}]"

        super().__init__(msg)


class RequirementError(Exception):
    pass


class SysCallError(Exception):
    def __init__(
        self,
        message: str,
        exit_code: int | None = None,
        worker_log: bytes = b"",
    ) -> None:
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.worker_log = worker_log


class ServiceException(Exception):
    pass


class PackageError(Exception):
    pass


class Deprecated(Exception):
    pass


class ConfigNotFound(FileNotFoundError):
    pass


class ThemeConfigError(Exception):
    pass
