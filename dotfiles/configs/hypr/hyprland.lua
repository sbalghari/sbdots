--  _   _                  _                 _
-- | | | |_   _ _ __  _ __| | __ _ _ __   __| |
-- | |_| | | | | '_ \| '__| |/ _` | '_ \ / _` |
-- |  _  | |_| | |_) | |  | | (_| | | | | (_| |
-- |_| |_|\__, | .__/|_|  |_|\__,_|_| |_|\__,_|
--        |___/|_|
--  ____        _    __ _ _
-- |  _ \  ___ | |_ / _(_) | ___  ___
-- | | | |/ _ \| __| |_| | |/ _ \/ __|
-- | |_| | (_) | |_|  _| | |  __/\__ \
-- |____/ \___/ \__|_| |_|_|\___||___/
--
-- SBDots
-- By: Saifullah Balghari


-- Configurations
require("hyprland/animation")
require("hyprland/decoration")
require("hyprland/enviromentvars")
require("hyprland/general")
require("hyprland/input")
require("hyprland/keybindings")
require("hyprland/misc")
require("hyprland/monitor")
require("hyprland/windowrules")


-- Startup Apps & Services
hl.on("hyprland.start", function()
    hl.exec_cmd("sbdotsctl waybar --start")
    hl.exec_cmd("systemctl --user start --now hyprpolkitagent")
    hl.exec_cmd("systemctl --user start --now sbdots-actionsd.service")
    hl.exec_cmd("systemctl --user start --now sbdots-clipboard-listenerd.service")
    hl.exec_cmd("systemctl --user start --now swaync.service")
    hl.exec_cmd("wl-paste --watch &")
    hl.exec_cmd("udiskie &")
    hl.exec_cmd("devify &")
    hl.exec_cmd("waypaper --restore &")
end)
