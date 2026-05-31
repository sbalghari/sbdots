hl.config({
    input = {
        kb_layout = "us",
        follow_mouse = 1,
        natural_scroll = false,
        sensitivity = 0,
        touchpad = {
            natural_scroll = true,
            disable_while_typing = true,
            middle_button_emulation = true,
        },
    },
})

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace"
})
