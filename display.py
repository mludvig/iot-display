#!/usr/bin/env python3

import time
from datetime import datetime
from threading import Thread
from io import BytesIO

import digitalio
import board

import requests
import adafruit_rgb_display.st7735 as st7735
from PIL import Image, ImageDraw, ImageFont

TIME_FORMAT = "%I:%M %p"
FONT_FILE = "fonts/bttf.ttf"
FONT_SIZE_TIME = 15
FONT_SIZE_TEXT = 60
FONT_SIZE_SUBTEXT = 10
WALLPAPER = "images/wallpaper.jpg"  # Initial image
WALLPAPER_CHANGE = 60   # Seconds

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
            rotation=180,
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
            print(f"Resizing from {image.width}x{image.height} to {self.width}x{self.height}")
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

class Display(Thread):
    MODES = ("clock", "message")
    MODE_IDLE = "clock"

    def __init__(self, messagebus):
        super().__init__(name="Display")

        self.driver = DisplayDriver()
        self.font_time = ImageFont.truetype(FONT_FILE, FONT_SIZE_TIME)
        self.font_text = ImageFont.truetype(FONT_FILE, FONT_SIZE_TEXT)
        self.font_subtext = ImageFont.truetype(FONT_FILE, FONT_SIZE_SUBTEXT)
        self.image = Image.open(WALLPAPER)  # Initial image

        # Only subscribe to messagebus after we have the initial image
        self.messagebus = messagebus
        self.messagebus.subscribe("Display", self.message_handler)

        self.set_mode(self.MODE_IDLE)

    def run(self):
        _last = None
        while True:
            time.sleep(0.1)

            image = None

            if 0 < self.mode_expire < time.time():
                self.set_mode(self.MODE_IDLE)

            if self.mode == "clock":
                text = datetime.strftime(datetime.now(), TIME_FORMAT).lstrip('0')
                if text == _last:
                    continue
                image = self.draw_clock(self.image, text)
                _last = text
            elif self.mode == "message":
                if self.mode_data == _last:
                    continue
                image = self.draw_message(self.image, self.mode_data)
                _last = self.mode_data

            if image:
                self.driver.display_image(image)

    def message_handler(self, component, message, payload={}):
        print(f"{self.name}: component={component} message={message} payload={payload}")
        if message == "display-message":
            self.set_mode("message", data=payload)
        elif message == "refresh":
            self.update_image(payload['image'])
        else:
            print(f"{self.name}: Unknown message, ignored")

    def set_mode(self, mode, data={}):
        print(f"{self.name}: set_mode={mode} data={data}")
        if mode == "idle":
            mode = self.MODE_IDLE

        if mode not in self.MODES:
            print(f"{self.name}: Unknown mode: {mode}")
            return

        self.mode = mode
        self.mode_data = data

        expire = data.get('expire') # => None if not there
        if expire is None:
            self.mode_expire = -1
        else:
            self.mode_expire = time.time() + expire

    def update_image(self, image):
        self.image = image

    def draw_clock(self, image, text_time):
        # Draw into a new copy of the image
        image_draw = image.copy()
        draw = ImageDraw.Draw(image_draw)
        bbox = draw.textbbox((0,0), text=text_time, font=self.font_time, stroke_width=1)
        width = bbox[2]-bbox[0]
        height = bbox[3]-bbox[1]
        draw.text((image_draw.width/2 - width/2, image_draw.height - height - bbox[1] - 5), text_time, font=self.font_time, fill=(255,255,255), stroke_width=1, stroke_fill=(0,0,0))
        return image_draw

    def draw_message(self, image, payload):
        subtext = None
        subtext_color = None
        if isinstance(payload, dict):
            text = payload.get('text', '??')
            color = payload.get('color', 'yellow')
            subtext = payload.get('subtext', None)
            subtext_color = payload.get('subtext_color', color)
        elif isinstance(payload, str):
            text = payload
            color = 'orange'
        else:
            print(f"{self.name}: Invalid payload.")
            text = 'XXX'
            color = 'red'
        if subtext and not subtext_color:
            subtext_color = color

        # Draw into a new copy of the image
        image_draw = image.copy()
        draw = ImageDraw.Draw(image_draw)

        # Draw subtext - if any
        subtext_height_occupied = 0
        if subtext:
            subtext_bbox = draw.textbbox((0,0), text=subtext, font=self.font_subtext, stroke_width=1)
            subtext_width = subtext_bbox[2]-subtext_bbox[0]
            subtext_height = subtext_bbox[3]-subtext_bbox[1]
            subtext_height_occupied = subtext_height + subtext_bbox[1] + 5
            draw.text((image_draw.width/2 - subtext_width/2, image_draw.height - subtext_height_occupied), subtext, font=self.font_subtext, fill=subtext_color, stroke_width=1, stroke_fill=(0,0,0))

        # Draw main text
        text_bbox = draw.textbbox((0,0), text=text, font=self.font_text, stroke_width=1)
        text_width = text_bbox[2]-text_bbox[0]
        text_height = text_bbox[3]-text_bbox[1]
        draw.text((image_draw.width/2 - text_width/2, (image_draw.height - subtext_height_occupied)/2 - text_height/2), text, font=self.font_text, fill=color, stroke_width=1, stroke_fill=(0,0,0))

        return image_draw

class ImageDownloader(Thread):
    def __init__(self, messagebus, config):
        super().__init__(name="ImageDownloader")
        self.enabled = config.get('enabled', True)
        self.refresh_period = config.get('refresh', WALLPAPER_CHANGE)    # Download a new image every this many seconds
        self.url = config['url']
        self.messagebus = messagebus
        if self.enabled:
            print(f"{self.name}: Refresh image every {self.refresh_period} sec from {self.url}")

    def run(self):
        start_ts = time.time()
        while True:
            if self.enabled:
                self.download_image()
            time.sleep(self.refresh_period - ((time.time() - start_ts) % self.refresh_period))

    def download_image(self):
        try:
            r = requests.get(self.url)
            print(f"{self.name}: {r.url}")
            r.raise_for_status()
            image = Image.open(BytesIO(r.content))
            self.messagebus.publish("Display", "refresh", payload={"image": image})
        except Exception as e:
            print(f"{self.name}: {e}")

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
