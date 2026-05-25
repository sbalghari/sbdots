#!/usr/bin/env bash

mesg="Destination: $HOME/Pictures/Screenshots"

list_col='1'
list_row='5'
win_width='400px'

# Theme
theme="$HOME/.config/rofi/configs/dmenu.rasi"

option_1="  Capture Desktop"
option_2=" 󰩭 Capture Area"
option_3="  Capture Window"
option_4=" 󱎫 Capture in 5s"
option_5=" 󱎫 Capture in 10s"

# Rofi CMD
rofi_cmd() {
	rofi -theme-str "window {width: $win_width;}" \
		-theme-str "listview {columns: $list_col; lines: $list_row;}" \
		-theme-str 'textbox-prompt-colon {str: " ";}' \
		-dmenu \
		-p "Screenshot Menu" \
		-mesg "$mesg" \
		-markup-rows \
		-theme ${theme}
}

# Pass variables to rofi dmenu
run_rofi() {
	echo -e "$option_1\n$option_2\n$option_3\n$option_4\n$option_5" | rofi_cmd
}

dir="$HOME/Pictures/Screenshots"

if [[ ! -d "$dir" ]]; then
	mkdir -p "$dir"
fi

notify_view() {
	notify-send -u low --replace=699 "Screenshot Saved at $dir/$file"
}

shotnow() {
	hyprshot -m output -o "$dir"
	notify_view
}

shotarea() {
	hyprshot -m region -o "$dir"
	notify_view
}

shotwin() {
	hyprshot -m window -o "$dir"
	notify_view
}

shot5() {
	notify-send -t 1000 "Taking shot in: 5 seconds"
	sleep 5
	shotnow
}

shot10() {
	notify-send -t 1000 "Taking shot in: 10 seconds"
	sleep 10
	shotnow
}

run_cmd() {
	if [[ "$1" == '--opt1' ]]; then
		shotnow
	elif [[ "$1" == '--opt2' ]]; then
		shotarea
	elif [[ "$1" == '--opt3' ]]; then
		shotwin
	elif [[ "$1" == '--opt4' ]]; then
		shot5
	elif [[ "$1" == '--opt5' ]]; then
		shot10
	fi
}

chosen="$(run_rofi)"
case ${chosen} in
    $option_1)
		run_cmd --opt1
        ;;
    $option_2)
		run_cmd --opt2
        ;;
    $option_3)
		run_cmd --opt3
        ;;
    $option_4)
		run_cmd --opt4
        ;;
    $option_5)
		run_cmd --opt5
        ;;
esac
