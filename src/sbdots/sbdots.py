from importlib.metadata import PackageNotFoundError, version
import typer

from sbdots.lifecycle.installer import SBDotsInstaller
from sbdots.lifecycle.uninstaller import SBDotsUninstaller
from sbdots.lifecycle.updater import SBDotsUpdater
from sbdots.utils.logger import setup_logging


def get_sbdots_version() -> str:
    """Get the current version of SBDots from metadata file."""
    try:
        return version("treeva")
    except PackageNotFoundError:
        typer.echo("Warning: treeva package metadata not found.")
        return "unknown"


__version__ = get_sbdots_version()

cli = typer.Typer()
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


@cli.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the SBDots version",
        is_eager=True,
        callback=lambda v: (typer.echo(__version__) if v else None),
    ),
):
    pass

@cli.command()
def install(
    dry_run: bool = common_options[0],
    verbose: bool = common_options[1],
):
    _run(SBDotsInstaller, verbose, dry_run, "install")


@cli.command()
def uninstall(
    dry_run: bool = common_options[0],
    verbose: bool = common_options[1],
):
    _run(SBDotsUninstaller, verbose, dry_run, "uninstall")


@cli.command()
def update(
    dry_run: bool = common_options[0],
    verbose: bool = common_options[1],
):
    _run(SBDotsUpdater, verbose, dry_run, "update")


@cli.command("check-update")
def check_update(
    dry_run: bool = common_options[0],
    verbose: bool = common_options[1],
):
    _run(SBDotsUpdater, verbose, dry_run, "check_update")


if __name__ == "__main__":
    cli()
