#!/bin/bash
#Copies files from astroberry to your home directory
#run as DEST=/astrophotography/projects/M39/2021-06-09 ./rsync_to_local.sh 
DEST=${DEST:-/tmp}
while true
do
	#This has spurious failures so better not fail the script when it fails
	rsync -av astroberry:/camera $DEST
	#remove files older than a minute
	ssh astroberry "find /path -mmin +59 -type f -exec rm -fv {} \;"
	sleep 1
done

