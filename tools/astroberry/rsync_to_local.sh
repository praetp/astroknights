#!/bin/bash
#Copies files from astroberry to your home directory
#run as DEST=/astrophotography/projects/M39/2021-06-09 ./rsync_to_local.sh 
DEST=${DEST:-/tmp}
while true
do
	#This has spurious failures so better not fail the script when it fails
	#only copy files that are minimum 18MB (good indicator of whether files are complete)
	rsync -av --remove-source-files --min-size=18m astroberry:/camera $DEST
	sleep 1
done

