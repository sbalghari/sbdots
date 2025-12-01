# #!/bin/bash

# # Colors for output
# RED='\033[0;31m'
# GREEN='\033[0;32m'
# YELLOW='\033[1;33m'
# BLUE='\033[0;34m'
# NC='\033[0m' # No Color

# # Dependencies check
# dependencies=("figlet" "gum" "notify-send")
# missing_deps=()

# for dep in "${dependencies[@]}"; do
# 	if ! command -v "$dep" &>/dev/null; then
# 		missing_deps+=("$dep")
# 	fi
# done

# if [[ ${#missing_deps[@]} -gt 0 ]]; then
# 	echo -e "${RED} ERROR - Missing dependencies: ${missing_deps[*]}${NC}"
# 	echo "Please install the missing dependencies to continue."
# 	exit 1
# fi

# # AUR helper detection
# aur_helper=$(command -v yay || command -v paru || echo "")
# if [[ -z "$aur_helper" ]]; then
# 	echo -e "${RED} ERROR - No AUR helper found (yay or paru).${NC}"
# 	exit 1
# fi

# echo -e "${BLUE}Using AUR helper: $(basename "$aur_helper")${NC}"z
# echo

# # Title
# clear
# figlet -f smslant "System Updates"
# echo

# # Confirm update start
# if ! gum confirm "DO YOU WANT TO START THE SYSTEM UPDATE NOW?"; then
# 	echo -e "${YELLOW} Update canceled.${NC}"
# 	exit 0
# fi

# echo
# echo -e "${BLUE} Update started...${NC}"
# echo

# # Function to check if package is installed
# _isInstalled() {
# 	local package="$1"
# 	if $aur_helper -Qs "$package" | grep -q "local.*$package" 2>/dev/null; then
# 		return 0
# 	else
# 		return 1
# 	fi
# }

# # Function to run command with error handling
# _run_command() {
# 	local description="$1"
# 	local command="$2"

# 	echo -e "${YELLOW}▶ $description...${NC}"
# 	if eval "$command"; then
# 		echo -e "${GREEN}✓ $description completed${NC}"
# 		return 0
# 	else
# 		echo -e "${RED}✗ $description failed${NC}"
# 		return 1
# 	fi
# }

# # System updates
# _run_command "System update" "sudo pacman -Syu --noconfirm"

# # AUR updates
# _run_command "AUR update" "$aur_helper -Syu --noconfirm"

# # Cleanup orphaned packages
# echo
# if gum confirm "DO YOU WANT TO CLEAN UP ORPHANED PACKAGES?"; then
# 	orphans=$(pacman -Qdtq 2>/dev/null)
# 	if [[ -n "$orphans" ]]; then
# 		echo -e "${YELLOW}Orphaned packages found:${NC}"
# 		echo "$orphans"
# 		_run_command "Remove orphaned packages" "sudo pacman -Rns \$orphans --noconfirm"
# 	else
# 		echo -e "${GREEN}No orphaned packages found${NC}"
# 	fi
# else
# 	echo -e "${YELLOW}Skipping orphan cleanup${NC}"
# fi

# # Clean package cache
# echo
# if gum confirm "DO YOU WANT TO CLEAN PACKAGE CACHE? (Free disk space)"; then
# 	_run_command "Clean package cache" "sudo pacman -Sc --noconfirm"
# 	if [[ $(basename "$aur_helper") == "yay" ]]; then
# 		_run_command "Clean AUR cache" "yay -Sc --noconfirm"
# 	elif [[ $(basename "$aur_helper") == "paru" ]]; then
# 		_run_command "Clean AUR cache" "paru -Sc --noconfirm"
# 	fi
# fi

# # Final summary
# echo
# echo -e "${GREEN}=================================${NC}"
# echo -e "${GREEN}           UPDATE COMPLETE        ${NC}"
# echo -e "${GREEN}=================================${NC}"

# # Notify
# notify-send "System Update" "All updates completed successfully!" -i system-software-update

# # Reboot check
# echo
# if gum confirm "Updates complete. Some updates may require a reboot. Reboot now?"; then
# 	sudo reboot
# fi

# echo
# echo -e "${GREEN} All updates completed successfully!${NC}"
# echo
# echo -e "${BLUE}Press [ENTER] to close.${NC}"
# read -r
