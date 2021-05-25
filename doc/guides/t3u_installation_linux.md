# Introduction
The TP-Link T3U Archer is a small USB Wi-Fi adapter that is small enough for a raspberry pi 3B
so other USB ports are still usable.

# Installation procedure
The driver is not supported by default on Ubuntu 20.04 or astroberry 2.0.3.
Fortunately, it's easy to compile and install from sources.

```
# Update all packages per normal
sudo apt update
sudo apt upgrade

# Install prereqs
sudo apt install git dnsmasq hostapd bc build-essential dkms raspberrypi-kernel-headers

# Reboot just in case there were any kernel updates
sudo reboot

# Pull down the driver source
git clone https://github.com/cilynx/rtl88x2bu
cd rtl88x2bu/

# Configure for RasPi
sed -i 's/I386_PC = y/I386_PC = n/' Makefile
sed -i 's/ARM_RPI = n/ARM_RPI = y/' Makefile

# DKMS as above
VER=$(sed -n 's/\PACKAGE_VERSION="\(.*\)"/\1/p' dkms.conf)
sudo rsync -rvhP ./ /usr/src/rtl88x2bu-${VER}
sudo dkms add -m rtl88x2bu -v ${VER}
sudo dkms build -m rtl88x2bu -v ${VER} # Takes ~3-minutes on a 3B+
sudo dkms install -m rtl88x2bu -v ${VER}
```
