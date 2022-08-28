#!/bin/bash
#Partially inspired by https://davidmoulton.me/astronomy/astrophotography/2020/08/02/astrophotography-with-free-software.html
set -xEeuo pipefail

#This script will process flats, darks and lights.
#It's not a problem if flats and/or darks are missing
#If the input directories are named incorrectly (e.g. after copying from EKOS), this is not a problem.

#For now this script must be run from the directory where the Lights/ Flats/ .. directories are
SCRIPT_DIR=$(realpath $BASH_SOURCE)/../scripts


MASTER_FLAT_ARG=""
MASTER_DARK_ARG=""
BIAS_ARG=""
DRIZZLE="-drizzle"
DRIZZLE="" #uncomment to enable drizzle

if [ -d "process" ]; then
	rm -rf process
fi

#remove empty files
find -size 0 -print -delete

#make a separate directory for master calibration frames.
if [ ! -d "masters" ]; then
	mkdir masters
fi

if [ -d "Bias" ]; then
	#only create link if not empty
	if [ ! -e "biases" ]; then
		if [ ! -z "$(ls -A Bias)" ]; then
			ln -sf Bias biases
		fi
	fi
fi

#either take masterBias or use synthetic bias
if [ -e "masters/masterBias.fit" ]; then
	BIAS_ARG="-bias=../masters/masterBias"
elif [ -e "biases" ]; then
siril -s - << END_OF_SCRIPT
requires 0.99.10

# Convert Bias Frames to .fit files
cd biases
convert bias -out=../process
cd ../process

# Stack Bias Frames to bias_stacked.fit
stack bias rej 3 3 -nonorm -out=../masters/masterBias
cd ..
END_OF_SCRIPT
    BIAS_ARG="-bias=../masters/masterBias"
else 
	#For Canon
	#BIAS_ARG="-bias=\"=2048\""
	#For ZWO 533
	BIAS_ARG='-bias="=40*$OFFSET"'
	SYNTHBIAS=1
fi

if [ -d "Flat" ]; then
	find Flat -mindepth 1 -name "*.fits" -exec mv {} Flat \;
	#only create link if not empty
	if [ ! -e "flats" ]; then
		if [ ! -z "$(ls -A Flat)" ]; then
			ln -sf Flat flats
		fi
	fi
fi

if [ -f "masters/masterFlat.fit" ]; then
	echo "Reusing masterFlat"
	MASTER_FLAT_ARG="-flat=../masters/masterFlat"
elif [ -e "flats" ]; then

siril -s - <<END_OF_SCRIPT
requires 0.99.10

# Convert Flat Frames to .fit files
cd flats
convert flat -out=../process
cd ../process

# Pre-process Flat Frames
preprocess flat ${BIAS_ARG}

# Stack Flat Frames to pp_flat_stacked.fit
stack pp_flat rej 3 3 -norm=mul -out=../masters/masterFlat
cd ..
END_OF_SCRIPT

	rm -rf process
	MASTER_FLAT_ARG="-flat=../masters/masterFlat"
	echo "Using new masterFlat."
else
	echo "No flats to process. You may have vignetting and unwanted artifacts in the final result."
fi
#BIAS_ARG=""

if [ -d "Dark" ]; then
	#only create link if not empty
	if [ ! -e "darks" ]; then
		if [ ! -z "$(ls -A Dark)" ]; then
			ln -sf Dark darks
		fi
	fi
fi

if [ -f "masters/masterDark.fit" ]; then
	echo "Reusing masterDark"
	MASTER_DARK_ARG="-dark=../masters/masterDark"
	echo "Reusing existing masterDark."
elif [ -e "darks" ]; then
	siril -s ${SCRIPT_DIR}/makeMasterDark.ssf
	rm -rf process
	MASTER_DARK_ARG="-dark=../masters/masterDark"
	echo "Using new masterDark."
else
	echo "No darks to process. You may have elavated noise levels and/or hot pixels in the final result."
fi

if [ -d "Light" ]; then
	find Light -mindepth 1 -name "*.fits" -exec mv {} Light \;
	ln -sf Light lights
fi

if [[ "$INPUTTYPE" == "dualband" ]]; then
	echo "processing dualband input"
	PREPROCESS_OPTS="-equalize_cfa"
elif [[ "$INPUTTYPE" == "osc" ]]; then
	echo "processing osc input"
	PREPROCESS_OPTS="-equalize_cfa -debayer"
else
	echo "Unknown mode $INPUTTYPE. Pass either INPUTTYPE=osc or INPUTTYPE=dualband as env var."
	exit 1
fi



siril -s - <<END_OF_SCRIPT
requires 0.99.10

# Convert Light Frames to .fit files
cd lights
convert light -out=../process
cd ../process

# Pre-process Light Frames
preprocess light ${BIAS_ARG} ${MASTER_DARK_ARG} ${MASTER_FLAT_ARG} -cfa ${PREPROCESS_OPTS}
END_OF_SCRIPT

if [[ "$INPUTTYPE" == "dualband" ]]; then
	echo "processing Halpha"
siril -s - <<END_OF_SCRIPT_DUALBAND_HA
requires 0.99.10
cd process
seqsubsky pp_light 1
# Extract Ha and OIII
seqextract_HaOIII bkg_pp_light

# Align Ha lights
register Ha_bkg_pp_light -drizzle

# Stack calibrated Ha lights to Ha_result.fit
stack r_Ha_bkg_pp_light rej 3 3 -norm=addscale -output_norm -out=../Ha_result

END_OF_SCRIPT_DUALBAND_HA
	echo "processing OIII"
siril -s - <<END_OF_SCRIPT_DUALBAND_OIII
requires 0.99.10
cd process
# Align OIII lights
register OIII_bkg_pp_light -drizzle

# Stack calibrated Ha lights to OIII_result.fit
stack r_OIII_bkg_pp_light rej 3 3 -norm=addscale -output_norm -out=../OIII_result
cd ..

# Make linear match on OIII frame based upon Ha frame
load OIII_result
linear_match Ha_result 0 0.92
save OIII_result

END_OF_SCRIPT_DUALBAND_OIII
elif [[ "$INPUTTYPE" == "osc" ]]; then
siril -s - <<END_OF_SCRIPT_BG_OSC
requires 0.99.10
cd process

seqsubsky pp_light 1

close

END_OF_SCRIPT_BG_OSC
rm -rf process/pp* #save some space

siril -s - <<END_OF_SCRIPT_OSC
requires 0.99.10
cd process

# Align lights
register bkg_pp_light ${DRIZZLE}

# Stack calibrated lights to result.fit
#stack r_bkg_pp_light rej 3 3 -norm=addscale -output_norm -filter-wfwhm=90% -weighted -out=../result
stack r_bkg_pp_light rej 3 3 -norm=addscale -output_norm -filter-fwhm=4 -weighted -out=../result

cd ..
close

END_OF_SCRIPT_OSC
fi
echo "Processing completed successfully"
