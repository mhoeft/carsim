__author__ = 'mh'

from msgs.BasedMessage import BasedMessage


class BasedApplication(object):
    def __init__(self, env, name, interface):
        self.env = env
        self.name = name
        self.i = 0
        self.interface = interface
        self.application_interval = 0.1
        self.active = False

    def run(self):
        while True and self.active:
            yield self.env.process(self.send_beacon())

    def send_beacon(self):
        self.i += 1
        msg = BasedMessage(self.env)
        msg.data = self.name+" TEST ID: "+str(self.i)
        self.interface.send(msg)
        yield self.env.timeout(self.application_interval)