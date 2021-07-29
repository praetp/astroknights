#!/bin/bash
#Copies files from astroberry to your home directory
#run as DEST=/astrophotography/projects/M39/2021-06-09 ./rsync_to_local.sh 
DEST=${DEST:-/tmp}
rsync -av --remove-source-files astroberry:/camera $DEST
while true
do
	#This has spurious failures so better not fail the script when it fails
	#do not remove source files as it may remove files that are not complete yet
	rsync -av astroberry:/camera $DEST
	sleep 1
done

