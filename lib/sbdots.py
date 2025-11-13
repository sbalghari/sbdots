import sys
import argparse

from lifecycle.installer import SBDotsInstaller
from lifecycle.uninstaller import SBDotsUninstaller
from lifecycle.updater import SBDotsUpdater
from library import get_sbdots_version


DRY_RUN = False


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sbdots",
        description="SBDots, a polished, feature-rich ArchLinux + Hyprland Setup.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-i",
        "--install",
        action="store_true",
        help="Installs SBDots on your system",
    )
    group.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="Uninstalls SBDots from your system",
    )
    group.add_argument(
        "-u",
        "--update",
        action="store_true",
        help="Updates SBDots to the latest version",
    )
    group.add_argument(
        "-cu",
        "--check-update",
        action="store_true",
        help="Checks if a new version of SBDots is available",
    )
    group.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_sbdots_version(),
        help="Show program version and exit",
    )

    return parser


def handle_install() -> None:
    installer = SBDotsInstaller(dry_run=DRY_RUN)
    installer.install()


def handle_uninstall() -> None:
    uninstaller = SBDotsUninstaller(dry_run=DRY_RUN)
    uninstaller.uninstall()


def handle_update() -> None:
    updater = SBDotsUpdater(dry_run=DRY_RUN)
    updater.update()


def handle_check_update() -> None:
    updater = SBDotsUpdater(dry_run=DRY_RUN)
    updater.check_update()


def handle_no_command(parser) -> None:
    parser.print_help()
    sys.exit(0)


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.install:
        handle_install()
    elif args.remove:
        handle_uninstall()
    elif args.update:
        handle_update()
    elif args.check_update:
        handle_check_update()
    else:
        handle_no_command(parser)


if __name__ == "__main__":
    main()
