-- Variables
local mainMod = "SUPER"
local rofiApplets = "~/.config/rofi/applets"
local appLauncher = "rofi -show drun -theme $HOME/.config/rofi/launcher.rasi"

-----------------------
------ General --------
-----------------------

hl.bind(mainMod .. " + Q ", hl.dsp.window.close())  -- Exit The Focused Window
hl.bind(mainMod .. " + P ", hl.dsp.window.pseudo()) -- Toggle pseudo mode
hl.bind(mainMod .. " + A ", hl.dsp.window.float({
    action = "toggle"
}))                                                                                            -- Toggle floating mode
hl.bind(mainMod .. " + F ", hl.dsp.window.fullscreen())                                        -- Fullscreen The Active Window
hl.bind(mainMod .. " + SHIFT + C ", hl.dsp.exec_cmd("waypaper --random"))                      -- Change Wallpaper Randomly
hl.bind(mainMod .. " + SHIFT + P ", hl.dsp.exec_cmd("~/.config/hypr/scripts/color_picker.sh")) -- Color Picker
hl.bind(mainMod .. " + CTRL + R ", hl.dsp.exec_cmd("sbdotsctl waybar -rc"))                    -- Reload Waybar's configs
hl.bind(mainMod .. " + CTRL + T ", hl.dsp.exec_cmd("sbdotsctl waybar -r"))                     -- Reload Waybar
hl.bind(mainMod .. " + SPACE ", hl.dsp.exec_cmd(appLauncher))                                  -- Application Launcher
hl.bind(mainMod .. " + V ", hl.dsp.exec_cmd(rofiApplets .. "/clipboard.sh"))                   -- Clipboard Manager
hl.bind(mainMod .. " + SHIFT + S ", hl.dsp.exec_cmd(rofiApplets .. "/screenshot.sh"))          -- Screenshot Manager
hl.bind(mainMod .. " + SHIFT + Q ", hl.dsp.exec_cmd("wlogout"))                                -- Power Menu
hl.bind(mainMod .. " + E ", hl.dsp.exec_cmd("nautilus"))                                       -- Launch File Manager
hl.bind(mainMod .. " + RETURN ", hl.dsp.exec_cmd("kitty"))                                     -- Launch Terminal
hl.bind(mainMod .. " + SHIFT + escape ", hl.dsp.exec_cmd("kitty --class floating -e btop "))   -- Launch System Monitor

----------------------------------
------ Workspace & window --------
----------------------------------

-- Move Focus To The [Left | Right | Up | Down] Window
hl.bind(mainMod .. " + left ", hl.dsp.focus({
    direction = "left"
}))
hl.bind(mainMod .. " + right ", hl.dsp.focus({
    direction = "right"
}))
hl.bind(mainMod .. " + up ", hl.dsp.focus({
    direction = "up"
}))
hl.bind(mainMod .. " + down ", hl.dsp.focus({
    direction = "down"
}))

-- [Next | Previous] Non-Empty Workspace
hl.bind(mainMod .. " + Tab ", hl.dsp.focus({
    workspace = "m+1"
}))
hl.bind(mainMod .. " + SHIFT + Tab ", hl.dsp.focus({
    workspace = "m-1"
}))

-- Switch workspaces - mainMod + [0-9]
-- Move active window to a workspace with mainMod + SHIFT + [0-9]
-- Move All Windows from active Workspace To Workspace [1-9]
for i = 1, 10 do
    local key = i % 10 -- 10 maps to key 0
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({
        workspace = i
    }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({
        workspace = i
    }))
    hl.bind(mainMod .. " + CTRL + " .. key, hl.dsp.exec_cmd("~/.config/hypr/scripts/move_all.sh " .. i), {
        locked = true
    })
end

-- Move/resize windows with mainMod + LMB/RMB and dragging
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), {
    mouse = true
})
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), {
    mouse = true
})

------------------------------
------ Functions keys --------
------------------------------

-- Volume
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), {
    locked = true,
    repeating = true
})
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), {
    locked = true,
    repeating = true
})
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), {
    locked = true,
    repeating = true
})
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), {
    locked = true,
    repeating = true
})

-- LCD brightness
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd(
        "brightnessctl set 10%+ -m | awk -F ',' '{print $4+0}' | xargs -I[] notify-send -e -u low -h string:x-canonical-private-synchronous:brightness_notif -h int:value:[] '󰃠 Brightness: []%'"),
    {
        locked = true,
        repeating = true
    })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd(
        "brightnessctl set 10%- -m | awk -F ',' '{print $4+0}' | xargs -I[] notify-send -e -u low -h string:x-canonical-private-synchronous:brightness_notif -h int:value:[] '󰃠 Brightness: []%'"),
    {
        locked = true,
        repeating = true
    })

-- Playerctl
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), {
    locked = true
})
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), {
    locked = true
})
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), {
    locked = true
})
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), {
    locked = true
})
