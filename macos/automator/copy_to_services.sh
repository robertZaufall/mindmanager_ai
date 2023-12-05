#!/bin/bash

DESTINATION=~/Library/Services

# Create the destination directory if it doesn't exist
if [ ! -d "$DESTINATION" ]; then
    echo "Destination directory does not exist. Creating it now."
    mkdir -p "$DESTINATION"
fi

# Function to delete directories in destination that exist in source
delete_overlap() {
    for dir in $(ls -d */); do
        if [ -d "$DESTINATION/${dir}" ]; then
            echo "Deleting overlapping directory: $dir"
            rm -rf "$DESTINATION/${dir}"
        fi
    done
}

# Function to copy from source to destination
copy_to_destination() {
    rsync -av . "$DESTINATION"
}

# Delete the script from the destination after execution
delete_script() {
    rm -f "$DESTINATION/$(basename $0)"
}

# Main execution
delete_overlap
copy_to_destination
delete_script

echo "Copy completed."
