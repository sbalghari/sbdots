#!/bin/bash

# File containing clipboard history
history_file="$HOME/.cache/wl-clipboard-history"

# Theme
theme="$HOME/.config/rofi/configs/dmenu.rasi"

title="Clipboard History"

# Rofi command
rofi_cmd() {
    rofi -theme-str 'textbox-prompt-colon {str: "";}' \
        -theme-str 'window {width: 50%;}' \
        -theme "${theme}" \
        -p "$title" \
        -l 12 \
        -dmenu \
        -markup-rows
}

# Load clipboard history and pass to rofi
run_rofi() {
    if [[ -f "$history_file" ]]; then
        tac "$history_file" | rofi_cmd
    else
        echo "No clipboard history found." | rofi_cmd
    fi
}

# Copy the selected entry back to the clipboard
copy_to_clipboard() {
    selected="$1"
    if [[ -n "$selected" ]]; then
        echo -n "$selected" | wl-copy
        notify-send -u low "Clipboard" "Copied to clipboard: $selected"
    fi
}

# Main
chosen="$(run_rofi)"
if [[ -n "$chosen" ]]; then
    copy_to_clipboard "$chosen"
fi
