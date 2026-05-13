from __future__ import annotations

from pathlib import Path
import subprocess
from subprocess import CalledProcessError, CompletedProcess
from shutil import which
import shlex
import signal
import pexpect
import logging
import re
import sys
from typing import Callable, Dict, Any, Optional

from sbdots.utils.exceptions import CommandNotFound
from sbdots.utils.types import COMMAND
from sbdots.cli.ui.cli_utils import rinput, Spinner, print_error


def _sig_handler(signum, frame):
    raise TimeoutError


signal.signal(signal.SIGALRM, _sig_handler)


# RE for pexpect.expect for finding various sudo prompt patterns
PATTERNS = [
    re.compile(r"\[sudo\] password for .*:"),  # sudo password query prompt
    re.compile(
        r"Sorry, try again\.\s*\[sudo\] password for .*:"
    ),  # sudo retry password prompt
    re.compile(
        r"sudo: \d+ incorrect password attempts"
    ),  # sudo no password attempts left prompt
    re.compile(
        r"sudo: timed out reading password"
    ),  # sudo password query timeout prompt
    pexpect.EOF,
    pexpect.TIMEOUT,
]


def _pre_run(command: COMMAND, shell: bool) -> COMMAND:
    if not command:
        raise ValueError("Command must be a non-empty list of strings.")

    # Convert to a list if its a string
    if isinstance(command, str):
        command = shlex.split(command)

    # check if executable is installed
    executable = command[0] if command[0] != "sudo" else command[1]
    if not shell:
        if not which(executable):
            raise CommandNotFound(command=executable or command)

    # Convert Path objects to strings
    command = [str(arg) if isinstance(arg, Path) else arg for arg in command]

    return command


def _run(command: COMMAND, run_func: Callable[..., Any], kwargs: Dict[str, Any]) -> Any:
    """Base function to run commands"""
    command = _pre_run(command, kwargs.get("shell", False))

    str_cmd = shlex.join(command)

    try:
        return run_func(command, **kwargs)
    except FileNotFoundError as e:
        missing = e.filename or str_cmd
        raise CommandNotFound(
            command=missing, stderr=e.strerror, return_code=e.errno
        ) from e
    except CalledProcessError as e:
        msg = (
            f"Subprocess error running: {str_cmd}\n"
            f"returncode: {getattr(e, 'returncode', None)}\n"
            f"stdout: {getattr(e, 'stdout', None)}\n"
            f"stderr: {getattr(e, 'stderr', None)}"
        )
        raise RuntimeError(msg) from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error running: {str_cmd}\n{e}") from e


def run_command(
    command: COMMAND, shell: bool = False, check: bool = False
) -> CompletedProcess:
    """Run a command safely and return its result."""
    kwargs = {
        "text": True,
        "capture_output": True,
        "check": check,
        "shell": shell,
        "encoding": "utf-8",
    }
    return _run(command, subprocess.run, kwargs)


def check_output(
    command: COMMAND, shell: bool = False, timeout: Optional[float] = None
):
    """Run a command, capture and return its output"""
    kwargs = {
        "text": True,
        "timeout": timeout,
        "shell": shell,
        "encoding": "utf-8",
    }
    return _run(command, subprocess.check_output, kwargs)


def _handle_input(child, spinner, timeout: int = 300):
    """Password input handler for 'run_sudo_cmd'"""
    # disable logging to avoid logging the password
    log_snap = child.logfile
    child.logfile = None

    # set timeout
    signal.alarm(timeout)
    try:
        if spinner:
            pw = spinner.get_password()
        else:
            pw = rinput("[SUDO] Enter your password: ", password=True)

        if pw:
            child.sendline(pw)
            return 0  # success

    finally:
        signal.alarm(0)

    child.logfile = log_snap


def run_sudo_cmd(
    command: COMMAND,
    spinner: Optional[Spinner] = None,
    logger: Optional[logging.Logger] = None,
    ask_pass_threshold: Optional[int] = 3,
    verbose: bool = False,
) -> Optional[int]:
    """Run a privileged command and asks for password if sudo is not cached or expired and return process returncode"""

    if logger:
        logger.debug(f"Raw command: '{command}'")
    command = _pre_run(command, False)
    str_cmd = shlex.join(command)

    if logger:
        logger.debug(f"Processed str command: '{str_cmd}'")

    logfile = (
        open("/tmp/`sudo_output`.log", "w+", encoding="utf-8")
        if not verbose
        else sys.stdout
    )

    # spawn the child process
    child = pexpect.spawn(
        str_cmd,
        encoding="utf-8",
        echo=False,
        logfile=logfile,
    )

    if logger:
        logger.debug(f"Spawned the a child process, logging to: {logfile}")

    got_password = 0
    try:
        # poll for either a password prompt, EOF, or other output
        while child.isalive():
            # break if met threshold
            if ask_pass_threshold and got_password >= ask_pass_threshold:
                if logger:
                    logger.debug(f"Please stop asking for password, '{command[1]}'")
                break

            # check for any of the prompt patterns with a short timeout
            try:
                index = child.expect(pattern=PATTERNS, timeout=0.5)
            except pexpect.ExceptionPexpect:
                break

            # SUDO_PROMPTS matched: send password
            if index == 0:
                got_password += 1
                _handle_input(child, spinner)

            # SUDO_RETRY_PROMPTS matched: send password
            elif index == 1:
                got_password += 1
                _handle_input(child, spinner)

            # SUDO_ALL_ATTEMPTS_FAILED_PROMPTS or SUDO_TIMEOUT_PROMPTS matched: kill the child process if alive
            elif index == 2 or index == 3:
                if child.isalive():
                    child.close(force=True)
            else:
                if PATTERNS[index] == pexpect.TIMEOUT:
                    continue
                else:
                    break

    except KeyboardInterrupt:
        print_error(text="Error!", details="Process cancelled by the user.")
        return 1

    except TimeoutError:
        print_error(
            text="Error!",
            details="SUDO, timeout reading password, Please enter the password within 3 minutes next time.",
        )
        return 1

    finally:
        # cleanup
        if child.isalive():
            try:
                child.close(force=True)
            except Exception:
                pass

    rc = child.exitstatus
    if logger:
        logger.info(
            f"[green]Done.[/] exitstatus={rc} password_was_requested {got_password} times"
        )

    return rc
