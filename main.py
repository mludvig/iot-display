#!/usr/bin/env python3

import time

from threading import Thread, Timer, Event

import gpiozero

from display import Display

LED1 = "GPIO20"
LED2 = "GPIO21"
BUTTON = "GPIO16"

class Blinker(Thread):
    SLOW = 0.5
    FAST = 0.1

    def __init__(self, led1, led2):
        super(Blinker, self).__init__(name="Blinker")
        self.led1 = gpiozero.LED(led1)
        self.led2 = gpiozero.LED(led2)
        self.set_period(Blinker.SLOW)

    def run(self):
        while True:
            self.toggle()
            time.sleep(self.period)

    def toggle(self):
        self.led1.value = not self.led1.value
        self.led2.value = not self.led1.value

    def set_period(self, period):
        self.period = period
        print(f"Blinker: period set to {period}")

class Button(Thread):
    def __init__(self, button, events):
        super(Button, self).__init__(name="Button")
        self.button = gpiozero.Button(button)
        self.events = events

    def run(self):
        while True:
            print("Button: waiting for button press")
            self.button.wait_for_press()
            self.events["button_press"].set()
            self.events["button_press"].clear()
            self.button.wait_for_release()

class Controller(Thread):
    def __init__(self, blinker, display, events):
        super(Controller, self).__init__(name="Controller")
        self.blinker = blinker
        self.display = display
        self.events = events

    def run(self):
        import random
        while True:
            print("Controller: waiting for Event.button_press")
            self.events["button_press"].wait()
            self.blinker.set_period(self.blinker.FAST)
            self.blinker.toggle()
            self.display.display(random.choice(["img/yes.png", "img/nope.png", "img/maybe.png"]))
            self.blinker.set_period(self.blinker.SLOW)
        
if __name__ == "__main__":
    events = {
        "button_press": Event(),
        "display_done": Event(),
    }

    print("Starting Blinker")
    blinker = Blinker(LED1, LED2)
    blinker.start()

    print("Starting Button")
    button = Button(BUTTON, events)
    button.start()

    print("Creating Display")
    display = Display()

    print("Starting Controller")
    controller = Controller(blinker, display, events)
    controller.start()

    print("Startup done")
