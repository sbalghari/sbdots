#!/bin/bash

# Configuration
THEME="$HOME/.config/rofi/configs/dmenu.rasi"
FILTER_CONFIG="$HOME/.sbdots/settings/hyprshade_filter.sh"

# Check dependencies
if ! command -v hyprshade &>/dev/null; then
	notify-send "SBDots - Scripts" "Error: hyprshade is not installed"
	exit 1
fi

if ! command -v rofi &>/dev/null; then
	notify-send "SBDots - Scripts" "Error: rofi is not installed"
	exit 1
fi

# Get available shaders and add 'off' option
options="$(hyprshade ls)"$'\n'"  off"

# Use Rofi to display options
choice=$(echo "$options" | rofi -dmenu -i \
	-theme-str 'textbox-prompt-colon {str: "󱩍";}' \
	-no-show-icons \
	-l 8 \
	-width 30% \
	-p "Hyprshade" \
	-theme "$THEME")

# Exit if no selection made or user cancelled
if [ -z "$choice" ]; then
	exit 0
fi

# Clean the choice by removing any asterisks  and extra whitespace
choice=$(echo "$choice" | sed 's/^\*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')

# Check if user choice is already applied
if [ -f "$FILTER_CONFIG" ]; then
	source "$FILTER_CONFIG"
	if [ "$HYPRSHADE_FILTER" = "$choice" ]; then
		notify-send "SBDots - Scripts" "Shader '$choice' is already enabled"
		echo "Shader '$choice' is already enabled"
		exit 0
	fi
fi

# Save selection to config
mkdir -p "$(dirname "$FILTER_CONFIG")"
echo "HYPRSHADE_FILTER=\"$choice\"" >"$FILTER_CONFIG"

# Apply selection
if [ "$choice" = "off" ]; then
	hyprshade off
	notify-send "SBDots - Scripts" "Hyprshade deactivated"
	echo "Hyprshade turned off"
else
	if hyprshade on "$choice"; then
		notify-send "SBDots - Scripts" "Hyprshade shader: $choice"
		echo "Hyprshade activated with: $choice"
	else
		notify-send "SBDots - Scripts" "Error: Failed to apply shader: $choice"
		echo "Error: Failed to apply shader: $choice" >&2
		exit 1
	fi
fi
