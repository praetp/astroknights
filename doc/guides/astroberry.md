# Astroberry
This document contains some tips and tricks wrt Astroberry

## Disable onboard WiFi
Add `dtoverlay=disable-wifi` to /boot/config.txt.
This can save some power if you are not using the onboard Wi-Fi at all 
or you want to replace it with a USB dongle.

## Disable HDMI
`https://raspberrypi.stackexchange.com/a/82996/605`
