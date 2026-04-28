#!/bin/bash

# Dependencies check
dependencies=("figlet" "gum" "notify-send")
for dep in "${dependencies[@]}"; do
    if ! command -v "$dep" &>/dev/null; then
        echo " ERROR - Missing dependency: $dep"
        echo "Please install $dep to continue."
        exit 1
    fi
done

# AUR helper detection
aur_helper=$(command -v yay || command -v paru || echo "")
if [[ -z "$aur_helper" ]]; then
    echo " ERROR - No AUR helper found (yay or paru)."
    exit 1
fi

# Title
sleep 0.2
clear
figlet -f smslant "Updates"
echo

# Confirm update start
if gum confirm "DO YOU WANT TO START THE UPDATE NOW?"; then
    echo
    echo " Update started."
else
    echo
    echo " Update canceled."
    exit
fi

# Check if package is installed
_isInstalled() {
    package="$1"
    if $aur_helper -Qs --color always "$package" | grep -q "local.*$package"; then
        echo 0
    else
        echo 1
    fi
}

# System updates
sudo pacman -Syu --noconfirm

# AUR updates
$aur_helper

# Flatpak updates
if [[ $(_isInstalled "flatpak") == "0" ]]; then
    flatpak update
fi

# Cleanup orphaned packages
if gum confirm "DO YOU WANT TO CLEAN UP UNUSED PACKAGES?"; then
    sudo pacman -Rns $(pacman -Qdtq) --noconfirm
    echo " Orphaned packages removed."
fi

# Notify user
notify-send "Update complete"
echo
echo " Update complete"
echo
echo

echo "Press [ENTER] to close."
read
