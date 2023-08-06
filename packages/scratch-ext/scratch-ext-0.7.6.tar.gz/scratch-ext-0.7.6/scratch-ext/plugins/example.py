from base import PluginBase

class ExamplePlugin(PluginBase):

    def receive(self, message):
        # do something with the message, which will contain every broadcast
        # from scratch, for example 'broadcast pin 11 on'
        print message
        return True