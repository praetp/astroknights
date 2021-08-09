#!/bin/bash
#first start the server !
raspivid -v --nopreview -t 0 -o - | nc 192.168.1.223 5000
