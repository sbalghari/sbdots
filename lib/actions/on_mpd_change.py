from gi.repository.Playerctl import Player  # type: ignore
from gi.repository import Playerctl, GLib  # type: ignore

from pathlib import Path
from typing import List
import json

from utils.logger import Logger
from utils.paths import SBDOTS_LOG_DIR

import gi

gi.require_version("Playerctl", "2.0")


class OnMpdChange:
    is_long_running = True

    def __init__(self, conn, selected_player=None, excluded_player=[], *args):
        # Create logfile and setup logging
        self.logfile: Path = SBDOTS_LOG_DIR / "on_mpd_change.log"
        self.logfile.parent.mkdir(parents=True, exist_ok=True)
        self.logfile.unlink(missing_ok=True)
        self.logger = Logger(log_file=self.logfile)

        # Socket connection
        self.conn = conn

        # Mpd stuff
        self.manager = Playerctl.PlayerManager()
        self.loop = GLib.MainLoop()
        self.manager.connect(
            "name-appeared", lambda *args: self.on_player_appeared(*args)
        )
        self.manager.connect(
            "player-vanished", lambda *args: self.on_player_vanished(*args)
        )
        self.selected_player = selected_player
        self.excluded_player = excluded_player.split(",") if excluded_player else []

        self.init_players()

    def init_players(self):
        for player in self.manager.props.player_names:
            if player.name in self.excluded_player:
                continue
            if self.selected_player is not None and self.selected_player != player.name:
                self.logger.debug(
                    f"{player.name} is not the filtered player, skipping it"
                )
                continue
            self.init_player(player)

    def main(self):
        self.logger.info("Starting main loop")
        try:
            self.loop.run()
        except KeyboardInterrupt:
            self.logger.info("Received KeyboardInterrupt, stopping loop.")
            self.clear_output()

    def init_player(self, player):
        self.logger.info(f"Initialize new player: {player.name}")
        player = Playerctl.Player.new_from_name(player)
        player.connect("playback-status", self.on_playback_status_changed, None)
        player.connect("metadata", self.on_metadata_changed, None)
        self.manager.manage_player(player)
        self.on_metadata_changed(player, player.props.metadata)

    def get_players(self) -> List[Player]:
        return self.manager.props.players

    def write_output(self, text, title, player):
        self.logger.debug(f"Writing output: {text}")

        if self.conn.fileno() == -1:
            self.logger.debug("Connection already closed, skipping output")
            self.loop.quit()
            return

        output = {
            "text": text,
            "class": title + player.props.player_name,
            "alt": player.props.player_name,
        }

        try:
            self.conn.sendall(b"\n")
            self.conn.sendall((json.dumps(output) + "\n").encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            self.logger.warning(f"Connection lost: {e}. Stopping main loop.")
            self.loop.quit()

    def clear_output(self):
        if self.conn.fileno() == -1:
            self.logger.debug("Connection already closed, skipping clear")
            self.loop.quit()
            return

        try:
            self.conn.sendall(b"\n")
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            self.logger.warning(f"Connection lost: {e}. Stopping main loop.")
            self.loop.quit()

    def on_playback_status_changed(self, player, status, _=None):
        self.logger.debug(
            f"Playback status changed for player {player.props.player_name}: {status}"
        )
        self.on_metadata_changed(player, player.props.metadata)

    def get_first_playing_player(self):
        players = self.get_players()
        self.logger.debug(f"Getting first playing player from {len(players)} players")
        if len(players) > 0:
            # if any are playing, show the first one that is playing
            # reverse order, so that the most recently added ones are preferred
            for player in players[::-1]:
                if player.props.status == "Playing":
                    return player
            # if none are playing, show the first one
            return players[0]
        else:
            self.logger.debug("No players found")
            return None

    def show_most_important_player(self):
        self.logger.debug("Showing most important player")
        # show the currently playing player
        # or else show the first paused player
        # or else show nothing
        current_player = self.get_first_playing_player()
        if current_player is not None:
            self.on_metadata_changed(current_player, current_player.props.metadata)
        else:
            self.clear_output()

    def on_metadata_changed(self, player, metadata, _=None):
        self.logger.debug(f"Metadata changed for player {player.props.player_name}")
        player_name = player.props.player_name
        artist = player.get_artist()
        title = player.get_title()

        # Handle cases where title or artist is None
        if title is None:
            title = "Unknown Title"
        else:
            title = title.replace("&", "&amp;")

        if artist is None:
            artist = "Unknown Artist"

        track_info = ""
        if (
            player_name == "spotify"
            and "mpris:trackid" in metadata.keys()
            and ":ad:" in player.props.metadata["mpris:trackid"]
        ):
            track_info = "Advertisement"
        elif artist is not None and title is not None:
            track_info = " " + artist + " - " + title
        else:
            track_info = " " + player_name

        if track_info:
            if player.props.status != "Playing":
                track_info = " " + artist + " - " + title  # Use a paused icon

        # Only print output if no other player is playing
        current_playing = self.get_first_playing_player()
        if (
            current_playing is None
            or current_playing.props.player_name == player.props.player_name
        ):
            self.write_output(track_info, title, player)
        else:
            self.logger.debug(
                f"Other player {current_playing.props.player_name} is playing, skipping"
            )

    def on_player_appeared(self, _, player):
        self.logger.info(f"Player has appeared: {player.name}")
        if player.name in self.excluded_player:
            self.logger.debug(
                "New player appeared, but it's in exclude player list, skipping"
            )
            return
        if player is not None and (
            self.selected_player is None or player.name == self.selected_player
        ):
            self.init_player(player)
        else:
            self.logger.debug(
                "New player appeared, but it's not the selected player, skipping"
            )

    def on_player_vanished(self, _, player):
        self.logger.info(f"Player {player.props.player_name} has vanished")
        self.show_most_important_player()

    def stop(self) -> None:
        try:
            self.clear_output()
        finally:
            self.loop.quit()
            self.conn.close()
