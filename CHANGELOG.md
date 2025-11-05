# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
  - module `lib/modules/auto_power_saver.py

### Changed
  - Changed project name from HyprDots to SBDots

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
