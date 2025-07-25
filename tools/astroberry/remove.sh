#!/bin/bash 
set -xEeuo pipefail

REMOTE=astroberry.local
SRC=$1


if ping -c 1 ${REMOTE} > /dev/null; then
	rm -rf ${SRC}

	ssh ${REMOTE} "find /camera/${SRC}"
	read -p "OK to remove these files on astroberry ? (yes/no)" ANSWER
	if [ $ANSWER = "yes" ]; then
		ssh ${REMOTE} "rm -rf /camera/${SRC}"
		echo "Removal done" 

	fi
else 
	echo "${REMOTE} is not up" 
fi
