#!/bin/bash
set -e
#Copies files from astroberry to your home directory
#run as DEST=/astrophotography/projects/M39/2021-06-09 ./rsync_to_local.sh 
DEST=${DEST:-/camera}
while true
do
	set +e
	rsync -av astroberry:/camera $DEST
	rsync -av --copy-links --remove-source-files astroberry:logs/autofocus $DEST/camera/logs

	rsync -av --copy-links astroberry:logs/analyze $DEST/camera/logs
	rsync -av --copy-links astroberry:logs/indilogs $DEST/camera/logs
	rsync -av --copy-links astroberry:logs/kstarslogs $DEST/camera/logs
	rsync -av --copy-links astroberry:logs/focuslogs $DEST/camera/logs
	set -e
	sleep 1
done

