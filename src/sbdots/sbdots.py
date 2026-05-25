from logging import getLogger
from typing import Optional, Annotated
from importlib.metadata import PackageNotFoundError, version
import typer

from sbdots.lifecycle import SBDotsInstaller
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
    LOGGER_NAME = "SBDotsInitializer"

    setup_logging(
        LOGGER_NAME,
        verbose=verbose,
        use_rotating_file=True,
        file_handling_mode="a",
        log_file="SBDotsInstaller.log",
    )
    logger = getLogger(LOGGER_NAME)

    SBDotsInstaller(dry_run=dry_run, logger=logger, verbose=verbose).install()
