import json
import socket
import paho.mqtt.client
import paho.mqtt.publish

class MQTT:
    def __init__(self, messagebus, config):
        self.config = config

        self.server = config['server']
        self.port = config.get('port', 1883)
        self.topic = config['topic']
        self.client_name = config.get('client_name', 'is-he-coming')

        self.client = paho.mqtt.client.Client(self.client_name)

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
        self.messagebus.publish("MQTT", "message", payload=msg.payload.decode('ascii'))
