local colors = require("colors")

hl.config({
    decoration = {
        rounding = 8,
        active_opacity = 0.96,
        inactive_opacity = 0.82,
        fullscreen_opacity = 0.98,
        dim_inactive = false,
        dim_strength = 0.1,
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
