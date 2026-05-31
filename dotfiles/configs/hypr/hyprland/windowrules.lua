-- Applets
hl.window_rule({
    name  = "windowrule-1",
    match = {
        class = "(blueman-manager)|(org.pulseaudio.pavucontrol)",
    },
    move  = "monitor_w-monitor_w*0.305 40",
    float = true,
    size  = { "(monitor_w*0.3)", "(monitor_h*0.3)" },
})


-- Applications (i prefer them as floating)
hl.window_rule({
    name   = "windowrule-3",
    match  = {
        class =
        "(waypaper)|(org.gnome.Loupe)|(io.missioncenter.MissionCenter)|(org.kde.dolphin)|(org.gnome.Nautilus)|(vlc)|(com.github.th_ch.youtube_music)|(org.gnome.TextEditor)|(org.kde.ark)",
    },
    float  = true,
    center = 1,
    size   = { "(monitor_w*0.6)", "(monitor_h*0.6)" },
})

-- File dialogs
hl.window_rule({
    name  = "windowrule-8",
    match = {
        title =
        "(Open Folder)|(Open File)|(Save File)|(Save Folder)|(Save Image)|(Save As)|(Open As)|(Select file)|(Select folder)|(Open Archive)|(Sign in – Google accounts — Mozilla Firefox)",
    },
    float = true,
    size  = { "(monitor_w*0.6)", "(monitor_h*0.6)" },
})

-- Ignore maximize requests from all apps.
local suppressMaximizeRule = hl.window_rule({
    name           = "suppress-maximize-events",
    match          = { class = ".*" },

    suppress_event = "maximize",
})
suppressMaximizeRule:set_enabled(true)

-- Fix some dragging issues with XWayland
hl.window_rule({
    name     = "fix-xwayland-drags",
    match    = {
        class      = "^$",
        title      = "^$",
        xwayland   = true,
        float      = true,
        fullscreen = false,
        pin        = false,
    },

    no_focus = true,
})
