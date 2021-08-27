#!/bin/bash
#first start the server !
set -e
#Select 5 for wide FOV
#Select 1 for zoomed FOV

#raspivid -v --settings --exposure night -ISO 800 --hflip --vflip --nopreview -t 0 -o - | nc 192.168.1.12 5000
MODE=3 
ISO=3200
SHUTTER_TIME_US=200000
HOST=192.168.1.244

if ! ping -c 1 ${HOST};
then
	echo "$HOST unreacheable"
	exit 1
fi

#
raspivid -v --mode ${MODE} --settings --contrast 50 --exposure night --roi 0.35,0.35,0.5,0.5 --drc high -ISO ${ISO} -ss ${SHUTTER_TIME_US} --nopreview --vflip --hflip --flush -t 0 -o - | nc ${HOST} 5000
