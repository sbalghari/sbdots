from __future__ import annotations

import json
import socket
from abc import ABC, abstractmethod


class BaseAction(ABC):
    """
    Base action class for all SBDots actions.

    Every action must:
    - inherit BaseAction
    - implement main()
    - optionally implement stop()
    """
    def __init__(self, conn: socket.socket, *args: str):
        self.conn = conn
        self.args = args

    @abstractmethod
    def main(self) -> None:
        """
        Main action entrypoint.

        Use self.send() to communicate with daemon/client.
        """
        raise NotImplementedError

    def stop(self) -> None:
        """
        Optional graceful shutdown hook for long-running actions.
        """
        pass

    def send(self, data: dict | None = None) -> None:
        """
        Send structured response to daemon/client.
        """
        if data is None:
            data = {}

        try:
            encoded = (json.dumps(data) + "\n").encode()
            self.conn.sendall(encoded)

        except BrokenPipeError:
            # except (BrokenPipeError, ConnectionResetError, OSError):
            # Client disappeared
            pass

        except Exception as e:
            raise RuntimeError(f"Failed to send action response: {e}") from e
