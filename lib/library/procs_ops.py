import os
import psutil
import signal


def find_procs_by_name(name: str) -> psutil.Process | None:
    """Return the first process matching 'name'."""
    name = name.lower()
    for p in psutil.process_iter(["name", "exe", "cmdline"]):
        try:
            info = p.info
            if (
                info["name"]
                and info["name"].lower() == name
                or info["exe"]
                and os.path.basename(info["exe"]).lower() == name
                or info["cmdline"]
                and info["cmdline"][0].lower() == name
            ):
                return p
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None


def find_pid_by_name(name: str) -> int | None:
    """Return the PID of process 'name'."""
    proc = find_procs_by_name(name)
    return proc.pid if proc else None


def kill_proc_tree(
    pid: int,
    sig=signal.SIGTERM,
    include_parent: bool = True,
    timeout: float | None = None,
) -> bool:
    """Kill a process tree (including children).
    Returns True if all are dead, False otherwise."""
    if pid == os.getpid():
        raise RuntimeError("Refusing to kill myself.")

    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return True  # already dead

    procs = parent.children(recursive=True)
    if include_parent:
        procs.append(parent)

    # Send initial signal
    for p in procs:
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            continue

    gone, alive = psutil.wait_procs(procs, timeout=timeout)

    # Escalate if needed
    if alive:
        for p in alive:
            try:
                p.kill()  # force kill
            except psutil.NoSuchProcess:
                continue
        gone, alive = psutil.wait_procs(alive, timeout=3)

    return len(alive) == 0


def send_signal(procs_name: str, sig) -> bool:
    """Send a signal to a process by name.
    Returns True if successful, False if process doesn't exist or can't be signaled."""
    name = procs_name.lower()
    pid = find_pid_by_name(name)
    try:
        psutil.Process(pid).send_signal(sig)
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
