import click

from lifecycle.installer import SBDotsInstaller
from lifecycle.uninstaller import SBDotsUninstaller
from lifecycle.updater import SBDotsUpdater
from library import get_sbdots_version

__version__ = get_sbdots_version()


def common_options(func):
    options = [
        click.option("--dry-run/--no-dry-run", default=False),
        click.option("--verbose/--no-verbose", default=False),
    ]
    for opt in reversed(options):
        func = opt(func)
    return func


def _run(lifecycle_cls, verbose, dry_run, action):
    obj = lifecycle_cls(dry_run=dry_run, verbose=verbose)
    return getattr(obj, action)()


@click.group()
@click.version_option(version=__version__, message="%(version)s")
def cli():
    pass


@cli.command()
@common_options
def install(verbose, dry_run):
    _run(SBDotsInstaller, verbose, dry_run, "install")


@cli.command()
@common_options
def uninstall(verbose, dry_run):
    _run(SBDotsUninstaller, verbose, dry_run, "uninstall")


@cli.command()
@common_options
def update(verbose, dry_run):
    _run(SBDotsUpdater, verbose, dry_run, "update")


@cli.command()
@common_options
def check_update(verbose, dry_run):
    _run(SBDotsUpdater, verbose, dry_run, "check_update")
