import time
from threading import Thread
import gpiozero

class Button(Thread):
    def __init__(self, messagebus, button_pin):
        super().__init__(name="Button")
        self.button = gpiozero.Button(button_pin)
        self.messagebus = messagebus

    def run(self):
        while True:
            print("Button: waiting for button press")
            self.button.wait_for_press()
            self.messagebus.publish("Button", "pressed")

            print("Button: waiting for button release")
            self.button.wait_for_release()
            self.messagebus.publish("Button", "released")
