#!/bin/bash
#first start the server !
set -e
#Select 5 for wide FOV
#Select 1 for zoomed FOV

#raspivid -v --settings --exposure night -ISO 800 --hflip --vflip --nopreview -t 0 -o - | nc 192.168.1.12 5000
MODE=1 
SHUTTER_TIME_US=700000


raspivid -v --mode ${MODE} --settings --exposure night -ISO 1600 -ss ${SHUTTER_TIME_US} --nopreview --hflip --vflip --flush -t 0 -o - | nc 192.168.1.12 5000
