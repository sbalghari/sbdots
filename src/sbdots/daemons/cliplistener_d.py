import os
import shutil
import subprocess
import time
import signal
from fcntl import flock, LOCK_EX, LOCK_UN
import logging

from sbdots.library.logger import setup_daemon_logging
from sbdots.constants import (
    CACHE_FILE,
    MAX_ENTRIES,
    MAX_LENGTH,
)

setup_daemon_logging("SBDotsClipboardListener")
logger = logging.getLogger("SBDotsClipboardListener")

try:
    import setproctitle

    setproctitle.setproctitle("sbdots-cliphist-d")

except Exception as e:
    logger.warning(
        "An unexpected error while setting process title",
        extra={"daemon": "cliphist"},
        exc_info=e,
    )
    pass

# Event bool for graceful shutdown
running = True


def handle_sigterm(signum, frame):
    global running
    logger.info("Received signal %s, exiting...", signum)
    running = False


signal.signal(signal.SIGINT, handle_sigterm)
signal.signal(signal.SIGTERM, handle_sigterm)


def ensure_cache_file():
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CACHE_FILE.exists():
        CACHE_FILE.touch(mode=0o600)
        logger.info("Created cache file %s", CACHE_FILE)


def get_clip():
    """Return clipboard text (string) or None on error."""
    try:
        p = subprocess.run(
            ["wl-paste", "--no-newline"],
            capture_output=True,
            text=True,
            timeout=1,
        )
        if p.returncode != 0:
            return None
        return p.stdout.strip()
    except FileNotFoundError:
        logger.error("'wl-paste' not found. Install wl-clipboard.")
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        logger.exception("Unexpected error calling wl-paste: %s", e)
        return None


def read_history():
    """Return list of lines from the cache file."""
    ensure_cache_file()
    with open(CACHE_FILE, "r", encoding="utf-8", errors="ignore") as fh:
        try:
            flock(fh, LOCK_EX)
            lines = [line.rstrip("\n") for line in fh]
        finally:
            flock(fh, LOCK_UN)
    return lines


def write_history(lines):
    """Write 'lines' list to the cache file atomically."""
    tmp = CACHE_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8", errors="ignore") as fh:
        try:
            flock(fh, LOCK_EX)
            for line in lines:
                fh.write(line.replace("\n", " ") + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        finally:
            flock(fh, LOCK_UN)
    shutil.move(str(tmp), str(CACHE_FILE))


def append_clip(clip):
    """Append the new clip."""
    if not clip:
        logger.error("No clip to append...!")
        return False

    clip = clip.strip()
    if clip == "":
        logger.error("Empty clip...!")
        return False

    if len(clip) > MAX_LENGTH:
        logger.error("Clip too long to append...!")
        return False

    lines = read_history()
    if clip in lines:
        logger.info("'%s' is already in history, bringing it to the front...", clip)
        lines.remove(clip)
        lines.append(clip)
    else:
        lines.append(clip)

    if len(lines) > MAX_ENTRIES:
        # remove oldest entries
        lines = lines[-MAX_ENTRIES:]
    write_history(lines)
    return True


def main_loop():
    ensure_cache_file()
    last_clip = None

    while running:
        clip = get_clip()
        if clip is not None:
            if clip != last_clip:
                added = append_clip(clip)
                if added:
                    logger.info("Added clip | len: %d | clip: [%s]", len(clip), clip)
                last_clip = clip
        time.sleep(0.2)


def main():
    logger.info("Starting wl-clipboard-listener daemon...")
    try:
        logger.info("Started wl-clipboard-listener daemon!")
        main_loop()
    except Exception:
        logger.exception("wl-clipboard-listener daemon crashed")
        raise
    finally:
        logger.info("wl-clipboard-listener daemon stopped.")


if __name__ == "__main__":
    main()
