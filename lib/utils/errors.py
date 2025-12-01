##############################################
## Process related errors
##############################################
class ProcessNotKilled(Exception):
    """Raised when psutil is not successful at killing a process"""

    def __init__(self, pid, reason=None):
        self.pid = pid
        self.reason = reason
        msg = f"Failed to kill process {pid}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
