#!/bin/bash

# Download dir
DOWNLOAD_DIR="/tmp/sbdots"

# Main setup script
SETUP="$DOWNLOAD_DIR/setup/setup.py"

# Colors
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

# Colored output helpers
info() { echo -e "${YELLOW}> $1${RESET}"; }
success() { echo -e "${GREEN}✔ $1${RESET}"; }
fail() { echo -e "${RED}✘ $1${RESET}"; }

# Check if running as root
if [[ $EUID -eq 0 ]]; then
	fail "Don't run this script as root. Exiting..."
	exit 1
fi

# Check if running on arch
if [[ ! -f "/etc/arch-release" ]]; then
	fail "This script is designed for Arch Linux only"
	exit 1
fi

# Function to check if a package is installed
_is_installed() {
	local package="$1"
	pacman -Q "$package" >/dev/null 2>&1
}

# Create a dir
_create_dir() {
	local dir="$1"

	if [ ! -d "$dir" ]; then
		mkdir -p "$dir"
		success "Created directory: $dir"
		return 0
	fi

	if [ -z "$(ls -A "$dir")" ]; then
		info "Directory exists and is empty: $dir"
		return 0
	fi

	rm -rf "${dir:?}/"* "${dir:?}/".* 2>/dev/null || true
	info "Directory existed but was not empty. Emptied: $dir"
	return 0
}

# Function to install required dependencies of the setup script
_install_dependencies() {
	local deps=(curl git base-devel jq gum python-pyfiglet python-rich python-psutil)

	info "Installing required dependencies..."
	for dep in "${deps[@]}"; do
		if ! _is_installed "$dep"; then
			if ! sudo pacman -S --noconfirm "$dep"; then
				fail "Failed to install $dep. Manual install needed!"
				exit 1
			fi
		else
			info "$dep is already installed. Skipping..."
		fi
	done
	echo
}

# Function to install yay (AUR helper)
_install_yay() {
	info "Installing yay..."

	_create_dir "/tmp/yay"
	if git clone https://aur.archlinux.org/yay.git "/tmp/yay" >/dev/null 2>&1; then
		cd "/tmp/yay" || return 1
		if makepkg -si --noconfirm; then
			success "yay installed successfully"
			cd ~ >/dev/null || true
			rm -rf "/tmp/yay"
			return 0
		else
			fail "makepkg failed while building yay"
			cd ~ >/dev/null || true
			rm -rf "/tmp/yay"
			return 1
		fi
	else
		fail "Could not clone yay from AUR"
		rm -rf "/tmp/yay"
		return 1
	fi
}

# Function to download the latest pre-release of SBDots
_download_pre_release() {
	info "Fetching latest tag..."

	latest_tag=$(curl -s https://api.github.com/repos/sbalghari/SBDots/releases |
		jq -r '.[] | select(.prerelease==true) | .tag_name' |
		head -n1)

	if [[ -z "$latest_tag" || "$latest_tag" == "null" ]]; then
		fail "Failed to fetch latest pre-release tag."
		exit 1
	fi

	echo
	success "Fetched version: $latest_tag"
	echo

	_create_dir "$DOWNLOAD_DIR"

	if git clone --branch "$latest_tag" --depth 1 https://github.com/sbalghari/SBDots.git "$DOWNLOAD_DIR"; then
		success "Successfully cloned release $latest_tag"
	else
		fail "Failed to clone pre-release. Retry later!"
		exit 1
	fi
}

# Function to download the rolling release of SBDots
_download_rolling_release() {
	_create_dir "$DOWNLOAD_DIR"

	if git clone --depth 1 https://github.com/sbalghari/SBDots.git "$DOWNLOAD_DIR"; then
		success "Successfully cloned rolling release"
	else
		fail "Failed to clone rolling release."
		exit 1
	fi
}

# Function to run the actual setup
_run_setup() {
	if command -v python3 >/dev/null 2>&1; then
		python3 "$SETUP"
	elif command -v python >/dev/null 2>&1; then
		python "$SETUP"
	else
		fail "Python not found. Please install python."
		return 1
	fi
}

main() {
	if _install_dependencies; then
		success "Installed setup dependencies"
		echo
	fi

	if ! command -v "yay" >/dev/null 2>&1; then
		if _install_yay; then
			success "Installed yay (AUR helper)"
			echo
		else
			fail "Yay install failed, Please install it manually and try again!"
			exit 1
		fi
	else
		success "Yay already installed, skipping..."
	fi

	echo
	echo

	info "Choose a version to download."
	choice=$(gum choose "Pre-release" "Rolling")

	case "$choice" in
	"Pre-release")
		_download_pre_release
		echo "pre-release" >"$DOWNLOAD_DIR/release_type.txt"
		;;
	"Rolling")
		_download_rolling_release
		echo "rolling" >"$DOWNLOAD_DIR/release_type.txt"
		;;
	*)
		fail "Invalid choice. Exiting."
		exit 1
		;;
	esac

	# Check if setup script exists
	if [[ ! -f "$SETUP" ]]; then
		echo
		fail "Setup script not found at $SETUP, something went wrong!"
		exit 1
	fi

	if ! _run_setup; then
		fail "Main setup failed to run, manually run $SETUP"
		exit 1
	fi
}

main
