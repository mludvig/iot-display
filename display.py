#!/usr/bin/env python3

import digitalio
import board
import adafruit_rgb_display.st7735 as st7735
from PIL import Image, ImageDraw
from io import BytesIO

class DisplayDriver:
    # GPIO configuration
    CS_PIN = board.CE0
    DC_PIN = board.D25
    RESET_PIN = board.D24
    BL_PIN = board.D23
    
    # Display baudrate
    BAUDRATE = 32000000

    def __init__(self):
        self._display = st7735.ST7735S(
            spi=board.SPI(),
            rotation=0,
            bl=digitalio.DigitalInOut(self.BL_PIN),
            cs=digitalio.DigitalInOut(self.CS_PIN),
            dc=digitalio.DigitalInOut(self.DC_PIN),
            rst=digitalio.DigitalInOut(self.RESET_PIN),
            baudrate=self.BAUDRATE,
            x_offset=0,
            y_offset=0,
            width=160,
            height=128,
        )

        # we swap height/width to rotate it to landscape!
        if self._display.rotation % 180 == 90:
            self.height = self._display.width  
            self.width = self._display.height
        else:
            self.width = self._display.width
            self.height = self._display.height

    def display_image(self, image):
        """
        image: PIL Image() object
        """
        if image.width > self.width or image.height > self.height:
            # If any dimension is bigger than our display scale it down
            image_ratio = image.width / image.height
            screen_ratio = self.width / self.height
            if screen_ratio > image_ratio:
                scaled_width = image.width * self.height // image.height
                scaled_height = self.height
            else:
                scaled_width = self.width
                scaled_height = image.height * self.width // image.width
            image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
        
            # Center the image
            x = image.width // 2 - self.width // 2
            y = image.height // 2 - self.height // 2
            image = image.crop((x, y, x + self.width, y + self.height))
        
        # Display image.
        self._display.image(image)

if __name__ == "__main__":
    import time
    import requests
    
    display = DisplayDriver()
    #url = f"https://unsplash.it/{display.width}/{display.height}/?random"
    #url = f"https://picsum.photos/id/718/{display.width}/{display.height}"
    url = f"https://source.unsplash.com/random/{display.width}x{display.height}"

    while True:
        try:
            r = requests.get(url)
            print(r.url)
            r.raise_for_status()
            image = Image.open(BytesIO(r.content))
        except Exception as e:
            print(f"Exception: {e}")
            time.sleep(10)
            continue
        
        display.display_image(image)

        time.sleep(10)
