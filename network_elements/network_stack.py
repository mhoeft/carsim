__author__ = 'mh'

import simpy
from network_elements.WirelessPipe import BroadcastPipe
from addresses import MacAddress, IPv6Address
import world

from msgs.BasedMessage import AppMsg





class BasedLayer(object):
    def __init__(self,  name = "BasedLayer"):
        self.env = world.env
        self.name = name
        self.upper_layer = None
        self.lower_layer = None
        self.store = simpy.Store(self.env)
        self.proc = self.env.process(self.run())

    def handle_lower_msg(self, msg):
        print self.name + ": handle_lower_msg at %f " % self.env.now
        self.upper_layer.handle_lower_msg(msg)
        #yield self.env.process(self.upper_layer.handle_lower_msg(msg))

    def handle_upper_msg(self, msg):
        print self.name + ": handle_upper_msg at %f " % self.env.now
        self.lower_layer.handle_upper_msg(msg)
        #yield self.env.process(self.lower_layer.handle_upper_msg(msg))

    def run(self):
        yield self.env.timeout(0.00001)
        #while True:
            #yield self.env.process(self.send_beacon())

    def latency(self, msg):
        yield self.env.timeout(0.01)
        self.connection_manager.get(msg)

    def put(self, msg):
        self.env.process(self.latency(msg))

    def get(self):
        return self.store.get()

    def set_lower_layer(self, layer_instance):
        self.lower_layer = layer_instance
        layer_instance.upper_layer = self

    def set_upper_layer(self, layer_instance):
        self.upper_layer = layer_instance
        layer_instance.lower_layer = self


class BasedPhyLayer(BasedLayer, object):
    def __init__(self, *kwargs):
        super(BasedPhyLayer, self).__init__(*kwargs)
        self.transmit_buffer = simpy.Store(self.env)
        self.link_rate = 18.0 * 10**6
        self.active_sch_channel = True
        self.channel_changed = self.env.event()
        self.in_pipe = None
        self.out_pipe = None
        self.start()

    def set_aether(self, pipeline):
        self.in_pipe = pipeline.get_output_conn()
        self.out_pipe = pipeline

    def handle_upper_msg(self, msg):
        print self.name + ": handle_upper_msg at " + str(self.env.now)
        self.transmit_buffer.put(msg)

    def change_channel(self):
        while True:
            self.active_sch_channel = not self.active_sch_channel
            self.channel_changed.succeed()
            self.channel_changed = self.env.event()
            print "SCH active? %s at %f " % (str(self.active_sch_channel), self.env.now)
            yield self.env.timeout(0.05)

    def transmit(self):
        while True:
            if self.active_sch_channel:
                msg = yield self.transmit_buffer.get()
                msg_size = 512*8
                print "delay %f " % (msg_size/self.link_rate)
                yield self.env.timeout(msg_size/self.link_rate)
                if self.active_sch_channel:
                    print self.name + ": msg transmitted at %f " % self.env.now
                    self.out_pipe.put(msg)
            else:
                yield self.channel_changed

    def receive(self):
        while True:
            msg = yield self.in_pipe.get()
            print "\t\t\t" + self.name + ": msg received  at %f " % self.env.now
            self.upper_layer.handle_lower_msg(msg)

    def start(self):
        self.env.process(self.change_channel())
        self.env.process(self.transmit())
        self.env.process(self.receive())


class BasedApplicationLayer(BasedLayer, object):
    def __init__(self):
        self.name = "BasedApplicationLayer"
        self.upper_layer = None
        self.lower_layer = None
        self.env = world.env
        self.i = 0
        self.application_interval = 0.01
        self.active = True
        self.store = simpy.Store(self.env)
        self.proc = self.env.process(self.run())
        self.rcv_msg = 0
        self.snd_msg = 0
        self.bandwidth = []

    def run(self):
        while True and self.active:
            yield self.env.process(self.send_beacon())

    def send_beacon(self):
        self.i += 1
        self.snd_msg += 1
        msg = AppMsg("RSU1", "aaaa"+str(self.i))
        self.lower_layer.handle_upper_msg(msg)
        yield self.env.timeout(self.application_interval)

    def handle_lower_msg(self, msg):
        print self.name + ": handle_lower_msg at " + str(self.env.now)
        print msg.msg
        self.rcv_msg += 1
        self.bandwidth.append({"time": self.env.now, "data": self.rcv_msg })

class IPv6Stack(object):
    def __init__(self, env):
        self.env = env
        self.phy = BasedPhyLayer(self.env, "PHY")
        self.mac = BasedLayer(self.env, "MAC")
        self.network = BasedLayer(self.env, "NETWORK")
        self.app = BasedApplicationLayer(self.env)

    def initialize(self, pipeline):
        self.phy.set_upper_layer(self.mac)
        self.mac.set_upper_layer(self.network)
        self.network.set_upper_layer(self.app)
        self.phy.set_aether(pipeline)

    def handle_received_msg(self, msg):
        self.phy.handle_lower_msg(msg)




class Interface(object):
    def __init__(self, owner, name="InterfaceName"):
        self.name = name
        self.id = 1 #TODO
        self.phy_layer = None
        self.mac_layer = None
        self.mac_address = None
        self.ipv6_address = None
        self.linklayer_address = None
        self.owner = owner


    def set_mac_address(self, mac_addr=None):
        self.mac_address = MacAddress(mac_addr)

    def set_ipv6_address(self, ipv6_address, netmask):
        self.ipv6_address = IPv6Address(ipv6_address, netmask)

    def get_ipv6_address(self):
        return self.ipv6_address

    def handle_upper_msg(self, ipv6_msg):
        self.mac_layer.handle_upper_msg(ipv6_msg)

class dot11pInterface(Interface):
    def __init__(self, owner):
        super(dot11pInterface, self).__init__(owner, "11p")
        self.phy_layer = BasedPhyLayer("PHY")
        self.mac_layer = BasedLayer("MAC")
        self.set_mac_address()
        self.phy_layer.set_upper_layer(self.mac_layer)

    def handle_upper_msg(self, ipv6_msg):
        self.mac_layer.handle_upper_msg(ipv6_msg)


if __name__ == "__main__":
    import time
    print "TEST"
    env = simpy.Environment()
    bc_pipe = BroadcastPipe(env)
    A_ipv6 = IPv6Stack(env)
    A_ipv6.initialize(bc_pipe)
    B_ipv6 = IPv6Stack(env)
    B_ipv6.initialize(bc_pipe)
    B_ipv6.app.active = False
    start_time = time.time()
    env.run(until=1)
    print "finished in %f" % (time.time() - start_time)
    #ipv6.handle_received_msg("TEST")
    print A_ipv6.app.snd_msg
    print A_ipv6.app.rcv_msg
    print B_ipv6.app.snd_msg
    print B_ipv6.app.rcv_msg

    from pylab import *
    t_tables = []
    d_tables = []
    for d in A_ipv6.app.bandwidth:
        t_tables.append(d["time"])
        d_tables.append(d["data"])
    plot(t_tables, d_tables, "o")
    xlabel('sim. time (s)')
    ylabel('received data [bits]')
    grid(True)
    legend(loc=2)
    show()