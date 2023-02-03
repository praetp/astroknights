#!/bin/bash
#archive all old files
set -xEeuo pipefail

SRC=/astrophotography/projects

function onError() {
	logger -p user.warn "Archive of ${SRC} encountered an error"
}

function cleanup() {
	rm /tmp/astro.${USER}.lock
}

trap onError ERR

if [ -e /tmp/astro.${USER}.lock ]; then
	logger -p user.warn "Archiving of ${SRC} could not be started because another session is already in progress"
	exit 1
fi

trap cleanup EXIT

HOSTNAME=$(hostname)
REMOTE=osmc.local

if ping -c 1 ${REMOTE} > /dev/null; then
	touch /tmp/astro.${USER}.lock
	logger -p user.notice "Backup of ${HOME} started"
	TMPFILE=$(mktemp /tmp/files.XXXXX)
	#move files older than 500 days to other storage
	find ${SRC} -mtime +500 -type f > ${TMPFILE} 
       	rsync -va --stats --progress --delete --remove-source-files --files-from=${TMPFILE} / ${REMOTE}-rsync:/media/media/astrophotography &> /tmp/astro.${USER}.log
	logger -p user.notice "Backup of ${HOME} completed successfully"
else 
	logger -p user.warn "Backup of ${HOME} could not be started"
fi
