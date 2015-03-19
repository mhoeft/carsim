__author__ = 'Michal Hoeft'


from propagation_model import DualSlopeModel

import random



class BaseInterface(object):
    def __init__(self, env, owner):
        self.env = env
        self.owner = owner
        self.connection_manager = None
        self.frame_lost = 0
        self.frame_sent = 0
        self.frame_received = 0
        self.msg_table = []
        self.bandwidth = []
        self.received_data = 0
    def run(self):
        while True:
            yield self.env.process(self.send())

    def send(self, msg="TEST Msg"):
        #  "%s sending msg at %f" % (self.owner.name, self.env.now)
        msg.set_sender(self.owner)
        self.connection_manager.put(msg)
        self.frame_sent += 1

    def receive(self, msg):
        if random.random() < 0.8:
            distance = self.owner.position.calculate_distance(msg._source)
            if distance < 300:
                if msg._destination == None or msg._destination == self.owner:
                    #print "_________________________________________________________________"
                    #print  "\t\t\t%s receiving %s at %f" % (self.owner.name, msg, self.env.now)
                    self.frame_received += 1
                    self.received_data += msg.size
                    self.bandwidth.append({"time":self.env.now, "data": self.received_data })

                if self.owner.is_ap:
                    if msg not in self.msg_table:
                        self.send(msg)
                        self.msg_table.append(msg)

    def print_report(self):
        print "NODE %s Interface report" % (self.owner.name)
        print "Number of lost frames: ", self.frame_lost
        print "Number of sent frames: ", self.frame_sent
        print "Number of received frames: ", self.frame_received
        print self.bandwidth

class Dot11pInterface(BaseInterface):
    def __init__(self,  env, owner):
        super(Dot11pInterface, self).__init__(env, owner)
        self.propagation_model = DualSlopeModel.DualSlopeModel()

    def receive(self, msg):
        if msg._source != self.owner:
            distance = self.owner.position.calculate_distance(msg._source)
            if random.random() > self.propagation_model.calculatePER(distance, msg.size):
                    if msg._destination == None or msg._destination == self.owner:
                        #print "_________________________________________________________________"
                        #print  "\t\t\t%s receiving %s at %f" % (self.owner.name, msg, self.env.now)
                        self.frame_received += 1
                        self.received_data += msg.size
                        self.bandwidth.append({"time":self.env.now, "data": self.received_data })
                        #self.bandwidth.append({"time":self.env.now, "data":self.owner.position.x})
                    #if self.owner.is_ap:
                    #    if msg not in self.msg_table:
                    #        self.send(msg)
                    #        self.msg_table.append(msg)

    def print_report(self):
        print "NODE %s Interface report" % (self.owner.name)
        print "Number of lost frames: ", self.frame_lost
        print "Number of sent frames: ", self.frame_sent
        print "Number of received frames: ", self.frame_received
        print self.bandwidth
