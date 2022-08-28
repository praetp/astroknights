#!/bin/bash
set -e
ffmpeg -y -framerate 60 -pattern_type glob -i '*.JPG' -vcodec hevc_nvenc out.mp4
echo "Conversion done" 
