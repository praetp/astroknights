#!/bin/bash
#run this first
while true
do
	netcat -l -p 5000 | mplayer -fps 60 -cache 2048 -
done
