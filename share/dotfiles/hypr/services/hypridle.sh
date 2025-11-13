#!/bin/bash

get_hypridle_pid() {
    pgrep -x hypridle
}

kill_hypridle() {
    HYPRIDLE_PID=$(get_hypridle_pid)
    if [ -n "$HYPRIDLE_PID" ]; then
        sleep 0.1
        kill -9 "$HYPRIDLE_PID"
        sleep 0.5
        echo "Hypridle killed."
    else
        echo "Hypridle is not running."
    fi
}

start_hypridle() {
    HYPRIDLE_PID=$(get_hypridle_pid)
    if [ -z "$HYPRIDLE_PID" ]; then
        hypridle &
        sleep 0.2
        echo "Hypridle started."
    else
        echo "Hypridle is already running."
    fi
}

toggle_hypridle() {
    HYPRIDLE_PID=$(get_hypridle_pid)
    if [ -n "$HYPRIDLE_PID" ]; then
        kill_hypridle
    else
        start_hypridle
    fi
}


case "$1" in
    kill)
        kill_hypridle
        ;;
    start)
        start_hypridle
        ;;
    toggle)
        toggle_hypridle
        ;;
    *)
        echo "Usage: $0 {kill|start|toggle}"
        exit 1
        ;;
esac

exit 0