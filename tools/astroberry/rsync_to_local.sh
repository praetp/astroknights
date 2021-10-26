#!/bin/bash
set -e
#Copies files from astroberry to your home directory
#run as DEST=/astrophotography/projects/M39/2021-06-09 ./rsync_to_local.sh 
DEST=${DEST:-/camera}
while true
do
	rsync -av --remove-source-files astroberry:/camera $DEST
	sleep 1
done

