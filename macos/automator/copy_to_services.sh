#!/bin/bash

set -e

SOURCE_DIR="."
DESTINATION=~/Library/Services

# Create the destination directory if it doesn't exist
if [ ! -d "$DESTINATION" ]; then
    echo "Destination directory does not exist. Creating it now."
    mkdir -p "$DESTINATION"
fi

workflows=(
    "MindManager AI.workflow"
)

for dir in "${workflows[@]}"; do
    target="$DESTINATION/$dir"
    source_dir="$SOURCE_DIR/$dir"

    if [ -d "$target" ]; then
        echo "Deleting $target"
        rm -rf "$target"
    fi

    if [ ! -d "$source_dir" ]; then
        echo "Source $source_dir not found." >&2
        exit 1
    fi

    echo "Copying $source_dir to $DESTINATION"
    cp -R "$source_dir" "$DESTINATION"
done

echo "Copy completed."
