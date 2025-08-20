#!/bin/bash
# Usage: ./startrails.sh output.jpg *.jpg
# Intermediate steps use TIFF (lossless, fast).

OUTPUT_FILE=$1
shift

# Detect correct ImageMagick command
if command -v magick >/dev/null 2>&1; then
    IM_CMD="magick"
elif command -v convert >/dev/null 2>&1; then
    IM_CMD="convert"
else
    echo "Error: ImageMagick not installed."
    exit 1
fi

# Temporary working file (TIFF, uncompressed for speed)
TEMP="temp_startrail.tif"
$IM_CMD "$1" -compress none "$TEMP"
shift

# Iteratively merge images
count=1
total=$#
for img in "$@"; do
    echo "[$count/$total] Merging $img ..."
    $IM_CMD "$TEMP" "$img" -evaluate-sequence max -compress none "temp_startrail.new.tif"
    mv "temp_startrail.new.tif" "$TEMP"
    count=$((count + 1))
done

# Final output — convert to requested format (JPG, PNG, etc.)
$IM_CMD "$TEMP" "$OUTPUT_FILE"
rm "$TEMP"

echo "✅ Star trail saved as $OUTPUT_FILE"

