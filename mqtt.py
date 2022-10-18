import json
import datetime
import paho.mqtt.client
import paho.mqtt.publish

from iputil import get_my_ip

class MQTT:
    def __init__(self, messagebus, config):
        self.config = config

        self.server = config['server']
        self.port = config.get('port', 1883)
        self.topic = config['topic']
        self.client_name = config.get('client_name', 'is-he-coming')

        self.client = paho.mqtt.client.Client(self.client_name)
        if config.get('username'):
            self.client.username_pw_set(config['username'], config.get('password'))

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.enable_logger()
        self.client.connect_async(self.server, port=self.port)
        self.client.loop_start()

        self.messagebus = messagebus

    def publish(self, topic, data):
        if not isinstance(data, (str, bytes)):
            data = json.dumps(data)
        self.client.publish(topic, data, qos=1, retain=True)

    def on_connect(self, client, userdata, flags, rc):
        print(f"MQTT: Connected")
        ret = client.subscribe(self.topic, 1)
        print(f"MQTT: Subscribed to: {self.topic} ({ret})")

    def on_message(self, client, userdata, msg):
        print(f"MQTT: {msg.topic}: {msg.payload}")
        payload = msg.payload.decode('ascii')
        self.messagebus.publish("MQTT", "message", payload=payload)
        self.publish(f"{msg.topic}/current", {
            "payload": payload,
            "timestamp": str(datetime.datetime.now().astimezone()),
            "ip": get_my_ip(),
        })
