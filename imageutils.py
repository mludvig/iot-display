#!/usr/bin/env python3

from datetime import datetime
from PIL import ImageFont, ImageDraw

TIME_FORMAT = "%I:%M %p"
FONT_FILE = "fonts/bttf.ttf"
FONT_SIZE = 15
font = ImageFont.truetype(FONT_FILE, FONT_SIZE)

def draw_time(image):
    draw = ImageDraw.Draw(image)
    text = datetime.strftime(datetime.now(), TIME_FORMAT)
    text = text.lstrip('0')
    bbox = draw.textbbox((0,0), text=text, font=font, stroke_width=1)
    width = bbox[2]-bbox[0]
    height = bbox[3]-bbox[1]
    draw.text((image.width/2 - width/2, image.height - height - bbox[1] - 5), text, font=font, fill=(255,255,255), stroke_width=1, stroke_fill=(0,0,0))
    return image
