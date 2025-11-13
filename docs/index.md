---
layout: home
pageClass: home-page

hero:
  name: "SBDots - A modern hyprland experience"

  image:
    src: /logo_dark.svg
    alt: sbdots logo
    style: "
      width: 200px; 
      height: auto; 
      border: 2px solid #1e1e2e33; 
      border-radius: 100%;
    "

  tagline: A dynamic, feature-rich and polished dotfiles for hyprland.

  actions:
    - theme: brand
      text: Get Started
      link: /getting_started/overview

    - theme: alt
      text: GitHub ↗
      link: https://github.com/sbalghari/sbdots

features:
  - icon: '<img width="35" height="35" src="https://cdn-icons-png.flaticon.com/128/5222/5222327.png" alt="aesthetics"/>'
    title: Aesthetics
    details: A clean, optimized configuration for Hyprland that ensures a visually appealing, efficient, and streamlined desktop experience.

  - icon: '<img width="35" height="35" src="https://cdn-icons-png.flaticon.com/128/2452/2452668.png" alt="functionality"/>'
    title: Functionality
    details: A modern status bar, launcher, and notification system, all bundled with automated installation for a smooth and user-friendly setup.

  - icon: '<img width="35" height="35" src="https://cdn-icons-png.flaticon.com/128/4729/4729487.png" alt="consistency"/>'
    title: Consistency
    details: A unified look across Hyprland, Waybar, SwayNC, and Flatpak apps by syncing seamlessly with the system-wide GTK theme.
---

## Quick Start

::: danger
**Alpha software** — expect rough edges. Currently supports **Arch Linux only**.
:::

### Prerequisites

Make sure you have:

- Arch Linux installed and updated.
- `git`, `bash`, `wget` available in your system.
- A backup of your current Hyprland/dotfiles (optional but recommended).

### Installation

Run the following command:

```bash
bash <(wget -qO- https://raw.githubusercontent.com/sbalghari/sbdots/main/install.sh)
```

Then, Follow the on-screen instructions.

### Post-Installation

- **Reboot** — recommended to apply all settings.
- Check that **Waybar**, **notifications**, and **launchers** are working.
- Refer to the [Wiki](/getting_started/overview) for detailed configuration and tweaks.
- Found any issue? Check the [FAQs](/help/faqs) or create a GitHub issue [here](https://github.com/sbalghari/sbdots/issues/new)
