import time
from threading import Thread
from gpiozero import LED

class Blinker(Thread):
    SLOW = 2
    FAST = 0.1
    IDLE = SLOW

    DEFAULT_EXPIRE = 30     # Expire red/green after DEFAULT_EXPIRE seconds

    def __init__(self, messagebus, led1, led2):
        super().__init__(name="Blinker")
        self.led1 = LED(led1)
        self.led2 = LED(led2)

        self.timer_expire = 0
        self.mode_expire = -1

        self.set_mode("idle")

        self.messagebus = messagebus
        self.messagebus.subscribe(component="Blinker", handler=self.message_handler)

    def run(self):
        while True:
            if 0 <= self.mode_expire <= time.time():
                self.set_mode("idle")
            if 0 <= self.timer_expire <= time.time():   # False if self.timer_expire==-1
                self.toggle()
                self.timer_expire = time.time() + self.period
            time.sleep(self.FAST)

    def message_handler(self, component, message, payload={}):
        print(f"{self.name}: component={component} message={message} payload={payload}")
        self.set_mode(message, payload.get('expire', self.DEFAULT_EXPIRE))

    def toggle(self):
        self.led1.value = not self.led1.value
        self.led2.value = not self.led1.value

    def set_period(self, period):
        print(f"Blinker: period set to {period}")
        self.period = period
        self.timer_expire = 0
        self.toggle()

    def set_mode(self, mode, expire=None):
        if expire is None:
            expire_ts = time.time()
            self.mode_expire = -1
        else:
            expire_ts = time.time() + expire
            self.mode_expire = expire_ts

        if mode == "idle":
            self.set_period(self.IDLE)
        elif mode == "fast":
            self.set_period(self.FAST)
        elif mode == "slow":
            self.set_period(self.SLOW)
        elif mode == "red":
            self.led1.value = False
            self.led2.value = True
            self.timer_expire = expire_ts
        elif mode == "green":
            self.led1.value = True
            self.led2.value = False
            self.timer_expire = expire_ts
        elif mode == "off":
            self.led1.value = False
            self.led2.value = False
            self.timer_expire = expire_ts
        else:
            print(f"{self.name}: Unknown mode: {mode}")
            return
