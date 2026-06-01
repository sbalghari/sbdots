local colors = require("colors")

hl.config({
    general = {
        gaps_in = 4,
        gaps_out = 5,
        gaps_workspaces = 0,
        border_size = 1,
        col = {
            active_border = colors.outline,
            inactive_border = colors.surface,
            nogroup_border_active = colors.outline,
            nogroup_border = colors.surface,
        },
        resize_on_border = true,
        extend_border_grab_area = 15,
        hover_icon_on_border = true,
        layout = "dwindle",
        no_focus_fallback = true,
        allow_tearing = false,
        snap = {
            enabled = true,
            window_gap = 5,
            monitor_gap = 5,
            border_overlap = true,
        },
    },
})
