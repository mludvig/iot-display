#!/bin/sh -x

# Python PIL / Pillow dependencies
sudo apt-get install ttf-dejavu libopenjp2-7 libtiff5

pip3 install --user --upgrade -r requirements.txt
