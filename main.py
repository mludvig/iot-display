#!/usr/bin/env python3

import sys
import os
import time
import logging

from PIL import Image, ImageOps

from lib import epd2in13d
from lib.image_tools import get_colour_mask, image_to_epd_data

picdir="img"

#Set output log level
logging.basicConfig(level=logging.DEBUG)

RED=(255, 0, 0)
WHITE=(255, 255, 255)
BLACK=(0, 0, 0)

try:
    logging.info("epd2in13d Demo")

    epd = epd2in13d.EPD()
    logging.info("Init and Clear")
    epd.init()
    #epd.Clear(0xFF)

    logging.info("Read Image File")
    img = Image.open(os.path.join(picdir, 'yes-c.png')).convert('RGB')
    img_ry = get_colour_mask(img, RED, BLACK, WHITE)
    img_b = get_colour_mask(img, WHITE, BLACK, WHITE)
    buf_ry = image_to_epd_data((img_ry))
    buf_b = image_to_epd_data((img_b))

    logging.info("Display image")
    epd.display(buf_b, buf_ry)

except Exception as e:
    logging.error(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")

finally:
    epd2in13d.epdconfig.module_exit()
    exit()
