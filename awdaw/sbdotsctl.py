import typer

from coreapi.waybarctl import cli_api as waybar

# Main typer app
cli = typer.Typer()

# Commands, every cli_api returns a typer app containing its subcommands
cli.add_typer(waybar(), name="waybar")
