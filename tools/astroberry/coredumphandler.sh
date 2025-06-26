#!/bin/bash -x
#this coredump handler will first park the mount and then call systemd-coredump

#should we check for kstars coredump or we just execute this for any crash ? Probaly good enough for now

logger "Crash detected! $(pwd)"
logger "Mount parking" 
#in fact not really needed if you use the indi watchdog
indi_setprop -h localhost EQMod\ Mount.TELESCOPE_PARK.PARK=On
logger "Calling systemd-coredump"
exec /usr/lib/systemd/systemd-coredump "$@" 
