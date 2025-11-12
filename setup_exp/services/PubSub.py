from collections import defaultdict


class PubSub:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, topic, callback):
        self.subscribers[topic].append(callback)

    def unsubscribe(self, topic, callback):
        if callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)

    def publish(self, topic, data):
        for callback in self.subscribers[topic]:
            callback(data)
