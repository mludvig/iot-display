#!/usr/bin/env python3

from button import Button
from blinker import Blinker
from display import Display
from messagebus import messagebus

LED1 = "GPIO20"
LED2 = "GPIO21"
BUTTON = "GPIO16"

class Controller:
    def __init__(self, messagebus):
        #super(Controller, self).__init__(name="Controller")
        self.messagebus = messagebus
        self.messagebus.subscribe(None, self.message_handler)   # None = subscribe to the root topic

    def message_handler(self, component, message):
        if component == "Button":
            if message == "pressed":
                self.messagebus.publish("Blinker", "fast")
            elif message == "released":
                self.messagebus.publish("Blinker", "slow")
                self.messagebus.publish("Display", "refresh-button")

if __name__ == "__main__":
    print("Starting Blinker")
    blinker = Blinker(messagebus, LED1, LED2)
    blinker.start()

    print("Starting Button")
    button = Button(messagebus, BUTTON)
    button.start()

    print("Creating Display")
    display = Display(messagebus)
    display.start()

    print("Creating Controller")
    controller = Controller(messagebus)
    #controller.start()

    print("Startup done")
