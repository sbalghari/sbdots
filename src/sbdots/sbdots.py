from typing import Optional, Annotated
from importlib.metadata import PackageNotFoundError, version
import typer

from sbdots.lifecycle.installer import SBDotsInstaller
from sbdots.library.logger import setup_logging


def get_sbdots_version() -> str:
    """Get the current version of SBDots from metadata file."""
    try:
        return version("sbdots")
    except PackageNotFoundError:
        typer.echo("Warning: sbdots package metadata not found.")
        return "unknown"


def version_callback(version: bool):
    if version:
        typer.echo(get_sbdots_version())
        raise typer.Exit(0)


cli = typer.Typer(add_completion=False)

common_options = [
    typer.Option(False, "--dry-run/--no-dry-run", help="Run without making changes"),
    typer.Option(False, "--verbose/--no-verbose", help="Verbose output"),
]


def _run(lifecycle_cls, verbose: bool, dry_run: bool, action: str):
    LOGGER_NAME = f"SBDots{action.capitalize()}er"
    logger_initialized = False

    def _setup_logger(verbose: bool):
        nonlocal logger_initialized
        if logger_initialized:
            return
        setup_logging(
            LOGGER_NAME,
            verbose=verbose,
            use_rotating_file=True,
            file_handling_mode="a",
            log_file=f"{action}er.log",
        )
        logger_initialized = True

    _setup_logger(verbose)
    obj = lifecycle_cls(dry_run=dry_run, logger_name=LOGGER_NAME, verbose=verbose)
    return getattr(obj, action)()


@cli.callback(invoke_without_command=True, no_args_is_help=True)
def _(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            help="show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
): ...


@cli.command()
def init(
    dry_run: bool = common_options[0],
    verbose: bool = common_options[1],
):
    """
    Initialize sbdots for the current user
    """
    _run(SBDotsInstaller, verbose, dry_run, "install")
