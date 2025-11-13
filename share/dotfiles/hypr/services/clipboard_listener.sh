#!/bin/bash

# Cache file for clipboard history
cache_file="$HOME/.cache/wl-clipboard-history"
touch "$cache_file"

max_entries=30
max_length=50

while true; do
  # Get the current clipboard content
  clip=$(wl-paste --no-newline)

  # Check if the clipboard content is valid and not already in the history
  if [ -n "$clip" ] && [ "${#clip}" -lt "$max_length" ] && ! grep -qFx "$clip" "$cache_file"; then
    # If the history exceeds max_entries, remove the oldest entry
    if [ "$(wc -l <"$cache_file")" -ge "$max_entries" ]; then
      sed -i '1d' "$cache_file"
    fi

    # Append the new clip to the history
    echo "$clip" >>"$cache_file"
  fi

  sleep 0.2
done

exit 0