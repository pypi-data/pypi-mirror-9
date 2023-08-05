class GPIOBasicBroadcastEventHandler(object):

    def __init__(self, broadcast):
        self._broadcast = broadcast

    def broadcast(self, pin_num):
        message = {
            'pin': pin_num
        }
        return self._broadcast(message)


class GPIOCustomBroadcastEventHandler(object):

    def __init__(self, broadcast):
        self._broadcast = broadcast

    def broadcast(self, message):
        return self._broadcast(message)
