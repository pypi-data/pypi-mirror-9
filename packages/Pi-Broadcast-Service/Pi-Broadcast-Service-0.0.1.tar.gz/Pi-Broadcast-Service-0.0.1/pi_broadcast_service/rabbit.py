import json
import pika


class Publisher(object):

    def __init__(self, rabbit_url, exchange):
        self._rabbit_url = rabbit_url
        self._exchange = exchange
        self._connection = pika.BlockingConnection(pika.URLParameters(self._rabbit_url))
        self._channel = self._connection.channel()

    def send(self, routing_key, message):
        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=routing_key,
            body=json.dumps(message))

    def stop(self):
        self._connection.close()
