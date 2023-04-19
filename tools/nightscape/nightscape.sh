#!/bin/bash
set -xe
VCODEC=libx265 #software
VCODEC=hevc_nvenc #hardware
#ffmpeg -y -framerate 15 -pattern_type glob -i '*.jpg' -pix_fmt yuv420p -vcodec libx265 -crf 28 out.mp4
#ffmpeg -y -framerate 5 -pattern_type glob -i '*.jpg' -pix_fmt yuv420p out.mp4
ffmpeg -y -framerate 15 -pattern_type glob -i '*.jpg' -pix_fmt yuv420p -vcodec ${VCODEC} out.mp4
echo "Conversion done" 
