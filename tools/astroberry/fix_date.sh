#!/bin/bash
set -e
ssh astroberry.local "sudo date -s '$(LC_ALL=C date)'"
