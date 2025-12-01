# #!/usr/bin/env bash

# # Pick and auto-copy
# color=$(hyprpicker -a)

# echo "$color"

# if [[ "$color" ]]; then

#   image=/tmp/${color}.png

#   # Generate preview
#   convert -size 48x48 xc:"$color" "$image"

#   # Notify
#   notify-send -i "$image" "$color" "Copied to clipboard"
# fi

# exit 0
