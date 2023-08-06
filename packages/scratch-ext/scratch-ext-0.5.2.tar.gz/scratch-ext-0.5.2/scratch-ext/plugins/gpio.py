from base import PluginBase
try:
    import RPi.GPIO as pyGPIO
    supported = True
except:
    supported = False
import re
import logging
logger = logging.getLogger(__name__)

class GPIOPlugin(PluginBase):
    available = False
    commands = ['gpio', 'pin']
    pins = {}
    socket = None
    available = [3,5,7,8,10,11,12,13,15,16,18,19,21,22,23,24,26]

    def __init__(self, socket):
        logger.debug("Initializing...")
        if supported == False:
            logger.warn("This CPU is not supported, ignoring messages")
        else:
            pyGPIO.setmode(pyGPIO.BOARD)
            pyGPIO.setwarnings(False)
            pyGPIO.cleanup()
            self._initpins()
            self.socket = socket
            logger.info("Initialized succesful")

    def _initpins(self):
        for pin in self.available:
            self.pins[pin] = {'type': None, 'state': None}

    def receive(self, message):
        if not supported:
            return False

        # check if we need to process this command
        if any(command in message for command in self.commands):
            logger.debug('acting on: %s' % message)
            message = message.replace('broadcast ', '')
            message = message.replace('"','')
            message = message.lower()
            matches = re.search('(pin|gpio) ?(?P<no>[0-9]+).(?P<value>on|1|off|0|high|low)', str(message.strip()))
            if matches:
                self.pin(no=matches.groupdict(0)['no'], value=matches.groupdict(0)['value'])
        else:
            logger.debug('ignoring: %s' % message.strip())

    def tick(self):
        if not supported:
            return False
        # check all pin states
        for no, pin in self.pins.items():
            if pin['type'] != pyGPIO.OUT:
                state = self.pin(no)
                if pin['state'] != state:
                    self.pins[no]['state'] = state
                    cmd = 'sensor-update "pin %s" %s' % (no, state)
                    self.send(cmd)

    def pin(self, no, value=None):
        no = int(no)
        if value:
            high = ['on','1', 'high']
            low = ['off','0','low']
            if value in high:
                value = pyGPIO.HIGH
            if value in low:
                value = pyGPIO.LOW
            logger.debug("Setting Pin %s to %s" % (no, value))
            # if we're sending data, mark this channel as output
            self.pins[no]['type'] = pyGPIO.OUT
            pyGPIO.setup(no, pyGPIO.OUT)
            pyGPIO.output(no, value)
        else:
            self.pins[no]['type'] = pyGPIO.IN
            pyGPIO.setup(no, pyGPIO.IN)

            return pyGPIO.input(no)
