#!/bin/bash

WAYBAR_STYLES_PATH="$HOME/.config/waybar/styles"
CURRENT_STYLE="$HOME/.config/sbdots/settings/waybar_style.sh"

WAYBAR_STYLE="modern"

# Check if waybar_style.sh settings file exists and load
if [ -f "$CURRENT_STYLE" ]; then
    source "$CURRENT_STYLE"
fi

CONFIG_FILE="$WAYBAR_STYLES_PATH/$WAYBAR_STYLE/config"
STYLE_CSS="$WAYBAR_STYLES_PATH/$WAYBAR_STYLE/style.css"

# Ensure the style directory and files exist
if [ ! -d "$WAYBAR_STYLES_PATH" ]; then
    echo "Error: Waybar styles directory not found at $WAYBAR_STYLES_PATH"
    exit 1
fi
if [ ! -f "$CONFIG_FILE" ] || [ ! -f "$STYLE_CSS" ]; then
    echo "Error: Config or style file not found for style '$WAYBAR_STYLE'"
    exit 1
fi

get_waybar_pid() {
    pgrep waybar
}

kill_waybar() {
    WAYBAR_PID=$(get_waybar_pid)
    if [ -n "$WAYBAR_PID" ]; then
        killall waybar
        sleep 0.2
        echo "Waybar killed."
    else
        echo "Waybar is not running."
    fi
}

start_waybar() {
    WAYBAR_PID=$(get_waybar_pid)
    if [ -z "$WAYBAR_PID" ]; then
        waybar -c "$CONFIG_FILE" -s "$STYLE_CSS" &
        echo "WAYBAR_STYLE=$WAYBAR_STYLE" > "$CURRENT_STYLE"
        sleep 0.2
        echo "Waybar started with style '$WAYBAR_STYLE'."
    else
        echo "Waybar is already running."
    fi
}

toggle_waybar() {
    WAYBAR_PID=$(get_waybar_pid)
    if [ -n "$WAYBAR_PID" ]; then
        kill_waybar
    else
        start_waybar
    fi
}

reload_waybar() {
    WAYBAR_PID=$(get_waybar_pid)
    if [ -n "$WAYBAR_PID" ]; then
        pkill -SIGUSR2 waybar
        echo "Waybar reloaded."
    else
        echo "Waybar is not running. Starting it now..."
        start_waybar
    fi
}

case "$1" in
    -k | --kill)
        kill_waybar
        ;;
    -s | --start)
        start_waybar
        ;;
    -t | --toggle)
        toggle_waybar
        ;;
    -r | --reload)
        reload_waybar
        ;;
    -h | --help)
        echo "Usage: $0 [OPTION]"
        echo "Options:"
        echo "  -k, --kill      Kill Waybar"
        echo "  -s, --start     Start Waybar"
        echo "  -t, --toggle    Toggle Waybar"
        echo "  -r, --reload    Reload Waybar"
        echo "  -h, --help      Display this help message"
        exit 0
        ;;
    *)
        echo "Invalid option. Use -h/--help for more information."
        exit 1
        ;;
esac

exit 0