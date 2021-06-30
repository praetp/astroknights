#!/bin/bash
#Partially inspired by https://davidmoulton.me/astronomy/astrophotography/2020/08/02/astrophotography-with-free-software.html
set -xEeuo pipefail

#This script will process flats, darks and lights.
#It's not a problem if flats and/or darks are missing
#There is no support for biases currently, we use a hardcoded synthetic bias instead.
#If the input directories are named incorrectly (e.g. after copying from EKOS), this is not a problem.

#For now this script must be run from the directory where the Lights/ Flats/ .. directories are
SCRIPT_DIR=$(realpath $BASH_SOURCE)/../scripts


MASTER_FLAT_ARG=""
MASTER_DARK_ARG=""
BIAS_ARG=""

if [ -d "process" ]; then
	rm -rf process
fi

#make a separate directory for master calibration frames.
if [ ! -d "masters" ]; then
	mkdir masters
fi

if [ -d "Flats" ]; then
	ln -sf Flats flats
fi

if [ -f "masters/masterFlat.fit" ]; then
	echo "Reusing masterFlat"
	MASTER_FLAT_ARG="-flat=../masters/masterFlat"
elif [ -e "flats" ]; then
	siril -s ${SCRIPT_DIR}/makeMasterFlat.ssf
	rm -rf process
	MASTER_FLAT_ARG="-flat=../masters/masterFlat"
	echo "Reusing existing masterFlat."
else
	echo "No flats to process. You may have vignetting and unwanted artifacts in the final result."
fi

if [ -d "Darks" ]; then
	ln -sf Darks darks
fi

if [ -f "masters/masterDark.fit" ]; then
	echo "Reusing masterDark"
	MASTER_DARK_ARG="-dark=../masters/masterDark"
	echo "Reusing existing masterDark."
elif [ -e "darks" ]; then
	siril -s ${SCRIPT_DIR}/makeMasterDark.ssf
	rm -rf process
	MASTER_DARK_ARG="-dark=../masters/masterDark"
else
	echo "No darks to process. You may have elavated noise levels and/or hot pixels in the final result."
	BIAS_ARG="-bias=\"=2048\""
fi

if [ -d "Lights" ]; then
	ln -sf Lights lights
fi


siril -s - <<END_OF_SCRIPT
requires 0.99.10

# Convert Light Frames to .fit files
cd lights
convert light -out=../process
cd ../process

# Pre-process Light Frames
preprocess light ${BIAS_ARG} ${MASTER_DARK_ARG} ${MASTER_FLAT_ARG} -cfa -equalize_cfa -debayer

# Align lights
register pp_light

# Stack calibrated lights to result.fit
stack r_pp_light rej 3 3 -norm=addscale -output_norm -out=../result

cd ..
close

END_OF_SCRIPT
echo "Processing completed successfully"
