#!/bin/bash
set -e
if ! git diff-index --quiet HEAD; then
	echo "Please commit all files first before taking a backup."
	exit 1
fi
DST_DIR=$(git rev-parse --show-toplevel)/configs


#.indi
rsync -av --prune-empty-dirs --include "*/" --include "*.xml" --include "*.db" --exclude="*" astroberry.local:.indi ${DST_DIR}

#.ssh
rsync -av --prune-empty-dirs --include "*/" --include "authorized_keys" --exclude="*" astroberry.local:.ssh ${DST_DIR}

#.local
rsync -av --prune-empty-dirs --include "*/" --include "kstars*" --include "autostart" --exclude="*" astroberry.local:.ssh ${DST_DIR}

git add ${DST_DIR}
git commit -m "Backup of configs taken on $(date)" 
git push

echo "Backup created and pushed to upstream." 

