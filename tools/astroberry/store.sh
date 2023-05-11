#!/bin/bash 
set -Eeuo pipefail

REMOTE=astroberry.local
SRC=$1
DEST=${DEST:-/astrophotography/projects/DSO}


if ping -c 1 ${REMOTE} > /dev/null; then
	read -p "OK to remove process directory ? (yes/no)" ANSWER
	if [ $ANSWER = "yes" ]; then
		rm -rf ${SRC}/process
	fi
	OLDEST_LIGHT=$(find ${SRC}/Light -type f -printf '%TY%Tm%Td\n' | sort | head -n 1)
	DEST_FULL=${DEST}/${SRC}/${OLDEST_LIGHT}
	
	mkdir -p ${DEST_FULL}
	echo "Moving files (this can take a while)"
	mv ${SRC}/* ${DEST_FULL}
	rmdir ${SRC}

	ssh ${REMOTE} "find /camera/${SRC}"
	read -p "OK to remove these files ? (yes/no)" ANSWER
	if [ $ANSWER = "yes" ]; then
		ssh ${REMOTE} "rm -rf /camera/${SRC}"
		echo "Removal done" 

	fi

else 
	echo "${REMOTE} is not up" 
fi
