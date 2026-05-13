#!/bin/bash

config_file=~/.config/hypr/configs/keybindings.conf
theme=~/.config/rofi/configs/keybinds.rasi
keybinds=""

if [ ! -f "$config_file" ]; then
    echo "Keybinding config file not found at $config_file."
    exit 1
fi
echo "Reading from: $config_file"

while IFS= read -r line; do
    if [[ "$line" == bind* ]]; then
        # Replace placeholders and remove unnecessary parts
        line=$(echo "$line" | sed -E 's/\$mainMod/SUPER/g;s/(bind[[:space:]]*=[[:space:]]*|bindm[[:space:]]*=[[:space:]]*)//')
        
        # Split the line into keybinding and command
        IFS='#' read -r kb_str cm_str <<<"$line"
        IFS=',' read -r mod key <<<"$kb_str"

        # Format the keybinding entry
        item="${mod} + ${key}"$'\r'"${cm_str:1}"
        keybinds+="$item"$'\n'
    fi
done < "$config_file"

echo "$keybinds" | rofi -dmenu -i -theme-str 'textbox-prompt-colon {str: "󰘳 ";}'  -markup -p "Keybinds" -theme ${theme}
