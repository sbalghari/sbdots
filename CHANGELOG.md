# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Added actions `volume` and `brightness`

### Changed
- Refactored media control handlers for brightness and volume operations
- Updated system keybindings and configurations to use new actions

---

## [0.1.0] - 2026-06-01
### Added
- Hyprland configuration migration to Lua format for improved maintainability (#23).
- `freedownloadmanager-bin` to recommended packages list.
- ROADMAP.md for project planning and direction.
- PKGBUILD for Arch Linux packaging support.
- `sbdotsctl` command with waybar flags for enhanced control.
- Project logo (sbdots.svg) in assets.
- `sbdots-actions` daemon for managing system actions and automation.
- Ruff CI workflow for automatic code linting and formatting.

### Changed
- Renamed defaults config directory from `configs` to `defaults`.
- Migrated services to systemd services with updated post-install script (#20).
- Fully migrated theming system from pywal to matugen (#19).
- Reorganized module structure with various rewrites for better maintainability (#14).
- Changed project name from HyprDots to SBDots.
- Updated PKGBUILD: removed ark, renamed swww to awww.
- Improved Waypaper configuration with corrected wallpaper paths.
- Updated README.md documentation multiple times for clarity.
- Changed waybar commands from scripts to flags.

### Fixed
- Removed 'systemd' from required_dotfile_components constant.
- Fixed service name and post-install hook to use `start` instead of `enable`.
- Corrected `require()` usage in hypr*.lua files and adjusted matugen template path for hyprland.lua (#25).
- Fixed incomplete/incorrect configurations introduced by previous refactors.
- Corrected Waypaper's post_command value.
- Removed on_media_change action in favor of Waybar's built-in MPRIS module (#17).
- Changed incorrect cliphist path.
- Fixed invalid keybind's exec configuration.
- Fixed minor documentation typo.
- Resolved dependency issues and removed deprecated AUR packages from PKGBUILD.
- Removed usage of deprecated/unfinished actions in configs.

### Removed
- Ark from PKGBUILD.
- `on_media_change` action in favor of Waybar's built-in MPRIS module.

---

## [0.0.3-alpha] - 2025-09-14
### Added
- Config file for version, tag, and other metadata.
- Placeholders for update/uninstall workflows.
- Spinner support in package installer with sudo cache monitoring.

### Changed
- Migrated installation from shell scripts to Python for maintainability.
- Introduced package-based installation (HyprDots installs as a Linux package).
- Replaced `install.sh` with a lightweight bootstrap script.
- Restructured repository for clarity and modularity:
  - `share/` – dotfiles, wallpapers, assets  
  - `lib/` – Python installation and management code  
  - `bin/` – executables and binaries  
- Cleaned up `lib/main.py` with focused responsibilities.
- Updated `README.md` with new structure and installation steps.

### Removed
- `share/configs/.gitignore` in favor of a global `.gitignore`.

### Fixed
- Multiple bugs and quality issues across modules.

---

## [0.0.2-alpha] - 2025-03-25
### Added
- Installation script with dependency management and configuration setup.
- `nwg-dock-hyprland` with customized look.
- Scripts for tasks such as GTK theme switching and power profile management.

### Changed
- Rofi now adapts to the current GTK-3/4 theme (no more hardcoded colors).
- Various adjustments and enhancements in dotfiles.

### Fixed
- Minor bugs.

---

## [0.0.1-alpha] - 2025-03-06
### Added
- Initial release.
