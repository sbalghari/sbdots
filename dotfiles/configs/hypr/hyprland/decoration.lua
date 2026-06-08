local colors = require("colors")

hl.config({
    decoration = {
        rounding = 10,
        active_opacity = 0.90,
        inactive_opacity = 0.82,
        fullscreen_opacity = 0.94,
        dim_inactive = false,
        blur = {
            enabled = true,
            new_optimizations = true,
            size = 4,
            passes = 2,
            noise = 0.0,
            contrast = 0.8,
            brightness = 0.8,
            vibrancy = 0.1,
            vibrancy_darkness = 0.0,
            popups = false,
            special = false,
        },
        shadow = {
            enabled = true,
            range = 4,
            render_power = 2,
            scale = 1.0,
            color = colors.shadow,
            color_inactive = colors.surface,
        },
    },
})
