#!/bin/bash
set -e
ssh astroberry "sudo date -s '$(LC_ALL=C date)'"
