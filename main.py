#!/usr/bin/env python3

from button import Button
from blinker import Blinker
from buzzer import Buzzer
from display import Display
from mqtt import MQTT
from messagebus import messagebus

LED1 = "GPIO20"
LED2 = "GPIO21"
BUTTON = "GPIO16"

config = {
    "Button": {
        "gpio": "GPIO16",
    },
    "Blinker": {
        "led1": "GPIO20",
        "led2": "GPIO21",
    },
    "Buzzer": {
        "pin": "GPIO3",
    },
    "MQTT": {
        "server": "test.mosquitto.org",
        "port": 1883,
        "topic": "kiwila/coming",
        "client_name": "mlpi",
    },
}

class Controller:
    def __init__(self, messagebus):
        self.messagebus = messagebus
        self.messagebus.subscribe(None, self.message_handler)   # None = subscribe to the root topic
        self.last_mqtt_payload = ''

    def message_handler(self, component, message, **kwargs):
        print(f"Controller: component={component} message={message} kwargs={kwargs}")
        if component == "Button":
            if message == "pressed":
                self.messagebus.publish("Blinker", "fast", payload={"expire": 120}) # Expire fast-blinking after 2 mins at the latest
            elif message == "released":
                self.messagebus.publish("Display", "display-message", payload=self.mqtt_to_display(self.last_mqtt_payload))
                self.messagebus.publish("Buzzer", "play", payload={"tune": self.last_mqtt_payload})
                self.messagebus.publish("Blinker", self.mqtt_to_color(self.last_mqtt_payload, default='fast'), payload={"expire": 30})
        elif component == "MQTT":
            if message == "message" and 'payload' in kwargs:
                # Sanitise MQTT Payload
                payload = kwargs['payload'].lower()
                payload == {"true": "yes", "false": "no"}.get(payload, payload) # Map true->yes, false->no ;)
                if payload not in ('yes', 'no', 'unknown'):
                    print(f"Controller: Invalid MQTT payload: {payload}")
                    return
                self.last_mqtt_payload = payload
                self.messagebus.publish("Display", "display-message", payload=self.mqtt_to_display(self.last_mqtt_payload))
                self.messagebus.publish("Buzzer", "play", payload={"tune": self.last_mqtt_payload})
                self.messagebus.publish("Blinker", self.mqtt_to_color(self.last_mqtt_payload, default='fast'), payload={"expire": 30})

    def mqtt_to_color(self, mqtt_message, default=None):
        colormap = { "yes": "green", "no": "red" }
        return colormap.get(mqtt_message.lower(), default)

    def mqtt_to_display(self, mqtt_message):
        if mqtt_message.lower() == "yes":
            return {
                "text": "YES",
                "color": "green",
                "subtext": "michael's not coming",
                "subtext_color": "yellow",
                "expire": 30,
            }

        if mqtt_message.lower() == "no":
            return {
                "text": "NO",
                "color": "red",
                "subtext": "michael is coming",
                "subtext_color": "yellow",
                "expire": 30,
            }

        return {
            "text": "???",
            "color": "yellow",
            "subtext": "who knows...",
            "expire": 30,
        }

if __name__ == "__main__":
    print("Starting Blinker")
    blinker = Blinker(messagebus, LED1, LED2)
    blinker.start()

    print("Starting Button")
    button = Button(messagebus, BUTTON)
    button.start()

    print("Starting Buzzer")
    buzzer = Buzzer(messagebus, config['Buzzer'])
    buzzer.start()

    print("Creating Display")
    display = Display(messagebus)
    display.start()

    print("Creating MQTT client")
    mqtt = MQTT(messagebus, config['MQTT'])

    print("Creating Controller")
    controller = Controller(messagebus)
    #controller.start()

    print("Startup done")
