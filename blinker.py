import time
from threading import Thread
import gpiozero

class Blinker(Thread):
    SLOW = 2
    FAST = 0.1

    DEFAULT_EXPIRE = 30     # Expire red/green after DEFAULT_EXPIRE seconds

    def __init__(self, messagebus, led1, led2):
        super(Blinker, self).__init__(name="Blinker")
        self.led1 = gpiozero.LED(led1)
        self.led2 = gpiozero.LED(led2)
        self.timer_expire = 0

        self.set_period(self.SLOW)

        self.messagebus = messagebus
        self.messagebus.subscribe(component="Blinker", handler=self.message_handler)

    def run(self):
        while True:
            if 0 <= self.timer_expire <= time.time():   # False if self.timer_expire==-1
                self.toggle()
                self.timer_expire = time.time() + self.period
            time.sleep(self.FAST)

    def message_handler(self, component, message, **kwargs):
        print(f"Blinker: component={component} message={message} kwargs={kwargs}")
        if message == "fast":
            self.set_period(self.FAST)
        elif message == "slow":
            self.set_period(self.SLOW)
        elif message == "red":
            self.led1.value = False
            self.led2.value = True
            self.timer_expire = time.time() + self.DEFAULT_EXPIRE
        elif message == "green":
            self.led1.value = True
            self.led2.value = False
            self.timer_expire = time.time() + self.DEFAULT_EXPIRE
        elif message == "off":
            self.led1.value = False
            self.led2.value = False
            self.timer_expire = -1

    def toggle(self):
        self.led1.value = not self.led1.value
        self.led2.value = not self.led1.value

    def set_period(self, period):
        print(f"Blinker: period set to {period}")
        self.period = period
        self.timer_expire = 0
        self.toggle()

