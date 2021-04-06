#!/usr/bin/env python3

import sys
import os
import time
import logging

from PIL import Image, ImageOps

from lib import epd2in13d
from lib.image_tools import split_image, image_to_epd_data

#Set output log level
logging.basicConfig(level=logging.DEBUG)

RED=(255, 0, 0)
WHITE=(255, 255, 255)
BLACK=(0, 0, 0)

class Display:
    def __init__(self):
        self.epd = epd2in13d.EPD()

    def display(self, image_file):
        try:
            logging.info(f"Read Image File: {image_file}")

            img = Image.open(image_file).convert('RGB')
            img_ry = split_image(img, RED, BLACK, WHITE)
            img_b = split_image(img, WHITE, BLACK, WHITE)

            logging.info("epd2in13d init")
            self.epd.init()
            #epd.Clear(0xFF)

            logging.info("Converting EPD data")
            buf_ry = image_to_epd_data(img_ry)
            buf_b = image_to_epd_data(img_b)

            logging.info("Display image")
            self.epd.display(buf_b, buf_ry)

        except Exception as e:
            logging.error(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")

        finally:
            #self.epd.display_off()
            pass

if __name__ == "__main__":
    display = Display()
    display.display(sys.argv[1])
