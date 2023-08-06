#!/usr/bin/env python -u
import logging
import traceback
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s: %(name)s - %(message)s")

import select
import threading
import errno
import socket
import time
import sys
import importlib

PORT = 42001
HOST = '127.0.0.1'
BUFFER_SIZE = 512
exitcode = 0

logging.info("Connecting...")
connected = False
while connected == False:
    try:
        scratchSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        scratchSock.connect((HOST, PORT))
        connected = True
    except:
        logging.warn('Connection failed, retrying, is Scratch Started?')
        connected = False
        time.sleep(1)
scratchSock.setblocking(False)
logging.info("Connected!")

# will hold all plugins
handlers = []

# start all plugins
import plugins
from plugins.base import PluginBase
import inspect

noload = ['__init__', 'base']
for plugin in plugins.__all__:
    if plugin in noload:
        continue

    module = importlib.import_module("plugins.%s" % plugin)
    pluginClassName = dir(module)[0]

    try:
        pluginClass = getattr(module, pluginClassName)
        if issubclass(pluginClass, PluginBase):
            handler = pluginClass(scratchSock)
            handlers.append(handler)
    except:
        # ignore any errors
        pass

logging.info('Found plugins: %s' % handlers)

class ScratchListener(threading.Thread):
    socket = None
    plugins = []

    def __init__(self, socket, plugins):
        threading.Thread.__init__(self)
        self.socket = socket
        self._stop = threading.Event()
        self.plugins = plugins

    def run(self):
        logging.debug("Started listening")
        while self.stopped() == False:
            try:
                data = scratchSock.recv(BUFFER_SIZE)
                # if we got any double messages, split them
                data = data.split('broadcast')

                for msg in data:
                    if len(msg.strip()) > 0:
                        logging.debug("Received: %s", msg)
                        for plugin in self.plugins:
                            plugin.receive(msg)
            except (KeyboardInterrupt, SystemExit):
                logging.warn("Thread received SystemExit")
                raise
            except socket.error, e:
                if e.args[0] == errno.EWOULDBLOCK: 
                    time.sleep(0.1)           # short delay, no tight loops
                else:
                    print e
                    break

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

listener = ScratchListener(scratchSock, handlers)
listener.start()

try:
    while True:
        logging.info('Tick')
        
        # check if connection is still up
        select.select([scratchSock,], [scratchSock,], [], 1)

        for plugin in handlers:
            plugin.tick()
        time.sleep(1)
except:
    exitcode = 1
    e = sys.exc_info()[0]
    traceback.print_exc()
finally:
    logging.info('Cleaning up...')
    listener.stop()
    listener.join(0)
    logging.debug('Stopped')
    sys.exit(exitcode)
