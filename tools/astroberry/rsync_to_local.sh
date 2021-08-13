#!/bin/bash
set -e
#Copies files from astroberry to your home directory
#run as DEST=/astrophotography/projects/M39/2021-06-09 ./rsync_to_local.sh 
DEST=${DEST:-/tmp}
while true
do
	rsync -av astroberry:/camera $DEST
	#remove files older than 5 minutes
	ssh astroberry "find /camera -mmin +5 -type f -exec rm -fv {} \;"
	sleep 1
done

