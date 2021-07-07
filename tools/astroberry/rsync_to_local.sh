#!/bin/bash
#Copies files from astroberry to your home directory
#run as DEST=/astrophotography/projects/M39/2021-06-09 ./rsync_to_local.sh 
while true
do
	#This has spurious failures so better not fail the script when it fails
	rsync -av --remove-source-files astroberry.local:/camera $DEST
	sleep 1
done

