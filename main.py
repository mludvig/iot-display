#!/usr/bin/env python3

import time
from threading import Thread, Timer, Event

import requests
import gpiozero
from PIL import Image
from io import BytesIO

from display import DisplayDriver
from messagebus import MessageBus, ButtonMessage, DisplayMessage

LED1 = "GPIO20"
LED2 = "GPIO21"
BUTTON = "GPIO16"

class Blinker(Thread):
    SLOW = 10
    FAST = 0.1

    def __init__(self, messagebus, led1, led2):
        super(Blinker, self).__init__(name="Blinker")
        self.led1 = gpiozero.LED(led1)
        self.led2 = gpiozero.LED(led2)
        self.timer_expire = 0

        self.set_period(self.SLOW)

        self.messagebus = messagebus
        self.messagebus.add_handler(ButtonMessage, self.message_handler)

    def run(self):
        while True:
            if time.time() >= self.timer_expire:
                self.toggle()
                self.timer_expire = time.time() + self.period
            time.sleep(self.FAST)

    def message_handler(self, message):
        assert isinstance(message, ButtonMessage)
        if message.action == ButtonMessage.PRESSED:
            self.set_period(self.FAST)
        elif message.action == ButtonMessage.RELEASED:
            self.set_period(self.SLOW)

    def toggle(self):
        self.led1.value = not self.led1.value
        self.led2.value = not self.led1.value

    def set_period(self, period):
        print(f"Blinker: period set to {period}")
        self.period = period
        self.timer_expire = 0
        self.toggle()

class Button(Thread):
    def __init__(self, messagebus, button):
        super(Button, self).__init__(name="Button")
        self.button = gpiozero.Button(button)
        self.messagebus = messagebus

    def run(self):
        while True:
            print("Button: waiting for button press")

            self.button.wait_for_press()
            message = ButtonMessage(action=ButtonMessage.PRESSED)
            self.messagebus.handle(message)

            print("Button: waiting for button release")
            self.button.wait_for_release()
            message = ButtonMessage(action=ButtonMessage.RELEASED)
            self.messagebus.handle(message)

class Display(Thread):
    def __init__(self, messagebus):
        super(Display, self).__init__(name="Display")
        self.disp = DisplayDriver()
        self.messagebus = messagebus
        self.messagebus.add_handler(ButtonMessage, self.message_handler)
        self.messagebus.add_handler(DisplayMessage, self.message_handler)
        self.url = f"https://source.unsplash.com/random/{self.disp.width}x{self.disp.height}"

    def run(self):
        message = DisplayMessage(None)
        while True:
            self.messagebus.handle(message)
            time.sleep(10)

    def message_handler(self, message):
        print(f"Display: received: {message}")
        try:
            r = requests.get(self.url)
            print(r.url)
            r.raise_for_status()
            image = Image.open(BytesIO(r.content))
        except Exception as e:
            print(f"Exception: {e}")
            return
        
        self.disp.display_image(image)

if __name__ == "__main__":
    print("Creating MessageBus")
    messagebus = MessageBus()

    print("Starting Blinker")
    blinker = Blinker(messagebus, LED1, LED2)
    blinker.start()

    print("Starting Button")
    button = Button(messagebus, BUTTON)
    button.start()

    print("Creating Display")
    display = Display(messagebus)
    display.start()

    print("Startup done")
