import threading
import logging
logger = logging.getLogger(__name__)

class PluginBase(object):
    available = False
    socket = None

    def __init__(self, socket):
        self.socket = socket
        # do setup stuff
        pass

    def tick(self):
        pass

    def receive(self, message):
        pass

    def send(self, cmd):
        n = len(cmd)
        b = (chr((n >> 24) & 0xFF)) + (chr((n >> 16) & 0xFF)) + (chr((n >>  8) & 0xFF)) + (chr(n & 0xFF))
        logger.debug('sending: %s' % cmd)
        return self.socket.send(b + cmd)
