import time
from rabbit import Publisher
from handler import GPIOBasicBroadcastEventHandler
from pi_pin_manager import PinManager


BROADCAST_EXCHANGE = 'gpio_broadcast'


class GPIOBasicBroadcastService(Publisher):

    def __init__(self, rabbit_url, device_key, pin_config):
        super(GPIOBasicBroadcastService, self).__init__(
            rabbit_url=rabbit_url,
            exchange=BROADCAST_EXCHANGE)

        self._device_key = device_key
        self._pin_config = pin_config
        self._pin_event_handler = GPIOBasicBroadcastEventHandler(self._broadcast)

    def _broadcast(self, message):
        return self.send(self._device_key, message)

    def start(self):
        try:
            self._pins = PinManager(
                config_file=self._pin_config,
                event_handlers=self._pin_event_handler)

            # This has to stay running for the GPIO threaded event callbacks
            while True:
                time.sleep(0.500)

        except:
            self.stop()
            raise

    def stop(self):
        try:
            self._pins.cleanup()
        except AttributeError:
            pass

        super(GPIOBasicBroadcastService, self).stop()


class GPIOCustomBroadcastService(GPIOBasicBroadcastService):

    def __init__(self, rabbit_url, device_key, pin_config, event_handler):
        super(GPIOCustomBroadcastService, self).__init__(
            rabbit_url=rabbit_url,
            exchange=BROADCAST_EXCHANGE)

        self._pin_event_handler = event_handler(self._broadcast)
