#!/bin/sh -x
# https://learn.adafruit.com/1-8-tft-display/python-wiring-and-setup#setup-3042417-27
sudo apt-get install ttf-dejavu
sudo apt-get install python3-pil	# Best to install via APT because it's got a lot of dependencies
sudo pip3 install -r requirements.txt
