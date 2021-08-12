#!/bin/bash
#opens the last file in the directory
eom $(ls -Art | tail -n 1)
