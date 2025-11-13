#!/bin/bash

theme=~/.config/rofi/configs/dmenu.rasi
filter=~/.config/sbdots/settings/hyprshade_filter.sh

if [[ "$1" == "rofi" ]]; then
    # List options
    options="$(hyprshade ls)\n  off"
    
    # Use Rofi to display options in a list view with proper styling  
    choice=$(echo -e "$options" | rofi -dmenu -i -theme-str 'textbox-prompt-colon {str: "󱩍";}'  -no-show-icons -l 6 -width 30 -p "Hyprshade" -theme ${theme})
    
    if [ ! -z "$choice" ]; then
        echo "hyprshade_filter=\"$choice\"" > ${filter}
        hyprshade on $choice
        if [ "$choice" == "  off" ]; then
            hyprshade off
            notify-send "Hyprshade deactivated"
            echo ":: hyprshade turned off"            
        else
            notify-send "Changing Hyprshade to $choice" "Shader applied successfully"
        fi
    fi
else
    # Default behavior when called outside of rofi (for activating or deactivating filters)
    hyprshade_filter="blue-light-filter-50"

    # Check if hyprshade.sh settings file exists and load
    if [ -f ${filter} ]; then
        source ${filter}
    fi

    # Toggle Hyprshade
    if [ "$hyprshade_filter" != "off" ]; then
        if [ -z "$(hyprshade current)" ]; then
            echo ":: hyprshade is not running"
            hyprshade on $hyprshade_filter
            notify-send "Hyprshade activated" "with $(hyprshade current)"
            echo ":: hyprshade started with $(hyprshade current)"
        else
            notify-send "Hyprshade deactivated"
            echo ":: Current hyprshade $(hyprshade current)"
            echo ":: Switching hyprshade off"
            hyprshade off
        fi
    else
        hyprshade off
        echo ":: hyprshade turned off"
    fi
fi
