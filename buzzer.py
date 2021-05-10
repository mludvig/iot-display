import time
from threading import Thread
from gpiozero import TonalBuzzer
from gpiozero.tones import Tone

class Buzzer(Thread):
    def __init__(self, messagebus, buzzer_pin, config):
        super().__init__(name="Buzzer")
        self.buzzer = TonalBuzzer(buzzer_pin)
        self.messagebus = messagebus
        if config.get('enabled', True):
            self.messagebus.subscribe(component="Buzzer", handler=self.message_handler)

    def message_handler(self, component, message, payload={}):
        print(f"{self.name}: component={component} message={message} payload={payload}")
        if message == "play":
            self.play(payload['tune'])
        else:
            print(f"{self.name}: Unknown message: {message}")

    def play(self, tune):
        tones = []
        if tune == "yes":
            tones = range(self.buzzer.min_tone.midi, self.buzzer.max_tone.midi)
        elif tune == "no":
            tones = range(self.buzzer.max_tone.midi, self.buzzer.min_tone.midi, -1)
        if not tones:
            return
        for tone in tones:
            self.buzzer.play(Tone(midi=tone))
            time.sleep(0.03)
        time.sleep(0.5)
        self.buzzer.stop()

if __name__ == "__main__":
    from messagebus import messagebus
    b = Buzzer(messagebus, "GPIO3")
    b.play('yes')
    time.sleep(1)
    b.play('no')
