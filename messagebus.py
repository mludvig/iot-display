#!/usr/bin/env python3

from pubsub import pub

class MessageBus:
    ROOT_TOPIC="root"
    _instance = None

    def __new__(cls):
        # Singleton initialisation
        if cls._instance is None:
            cls._instance = super(MessageBus, cls).__new__(cls)
            print("Created new MessageBus")
        return cls._instance

    def subscribe(self, component, handler):
        topic = f"{self.ROOT_TOPIC}"
        if component:
            topic += f".{component}"
        pub.subscribe(handler, topic)

    def publish(self, component, message, **kwargs):
        topic = f"{self.ROOT_TOPIC}"
        if component:
            topic += f".{component}"
        pub.sendMessage(topic, component=component, message=message, **kwargs)

messagebus = MessageBus()
print("messagebus: {}".format(id(messagebus)))
