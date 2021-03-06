#!/bin/bash
set -e
#Select 5 for wide FOV
#Select 1 for zoomed FOV

MODE=1 
SHUTTER_TIME_US=100000


raspivid -v --mode ${MODE} --settings --exposure night -ISO 800 -ss ${SHUTTER_TIME_US} --nopreview --hflip --vflip --flush -t 0 --codec MJPEG -l -o tcp://0.0.0.0:3333
