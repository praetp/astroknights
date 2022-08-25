#!/bin/bash
if ping -q -c 1 google.be; then
	find -L ~/logs -mindepth 1 -mtime +2 -delete
	logger "Cleanup done" 
else
	logger "Cannot reach google - probably datetime not correct then. Not cleaning..." 
fi
