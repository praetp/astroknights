#!/bin/bash
set -e
#starts vlc from command-line with minimal caching
cvlc --network-caching=0 tcp://astroberry:3333
