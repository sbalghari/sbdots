from typing import Optional
import subprocess
import threading
import time
import atexit


class SudoKeepAlive:
    def __init__(self, max_duration: Optional[int] = None):
        """
        Initialize sudo keep-alive.

        Args:
            interval: Seconds between sudo validations (default: 60)
            max_duration: Maximum duration in seconds before auto-stop (optional)
        """
        self.interval = 60
        self.max_duration = max_duration
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._is_running = False
        self._start_time: Optional[float] = None

    def start(self) -> None:
        """Ask for sudo once, then keep it alive in background."""
        with self._lock:
            if self._is_running:
                return  # Already running

            try:
                subprocess.run(
                    ["sudo", "-v"], check=True, capture_output=True, text=True
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to obtain sudo privileges: {e.stderr}")

            self._is_running = True
            self._start_time = time.time()
            self._stop.clear()
            self._thread = threading.Thread(target=self._keepalive, daemon=True)
            self._thread.start()
            atexit.register(self.stop)

    def _keepalive(self) -> None:
        """Background thread to maintain sudo privileges."""
        while not self._stop.is_set():
            time.sleep(self.interval)

            # Check if max duration has been exceeded
            if (
                self.max_duration is not None
                and self._start_time is not None
                and time.time() - self._start_time > self.max_duration
            ):
                self.stop()
                break

            try:
                subprocess.run(
                    ["sudo", "-v"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
            except subprocess.CalledProcessError:
                # Sudo authentication failed, stop the thread
                self._stop.set()
                break

    def stop(self) -> None:
        """Stop keepalive and invalidate sudo timestamp."""
        with self._lock:
            if not self._is_running:
                return

            self._stop.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=1.0)

            subprocess.run(
                ["sudo", "-k"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            self._is_running = False
            self._start_time = None
            atexit.unregister(self.stop)

    @property
    def is_running(self) -> bool:
        """Return whether the keepalive is active."""
        with self._lock:
            return self._is_running

    @property
    def elapsed_time(self) -> Optional[float]:
        """Return elapsed time since start in seconds, or None if not running."""
        with self._lock:
            if self._is_running and self._start_time:
                return time.time() - self._start_time
            return None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def restart(self) -> None:
        """Restart the keepalive mechanism."""
        self.stop()
        time.sleep(0.1)
        self.start()
