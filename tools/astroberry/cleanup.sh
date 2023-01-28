#!/bin/bash
set -ex
if ping -q -c 1 google.be; then
	#cleanup all logs
	find -L ~/logs/* -mindepth 1 -mtime +2 -delete
	#cleanup old empty dirs and files
	find /camera/ -type d -empty -print -delete -o -type f -empty -print -delete

	logger "Cleanup done" 
else
	logger "Cannot reach google - probably datetime not correct then. Not cleaning..." 
fi
