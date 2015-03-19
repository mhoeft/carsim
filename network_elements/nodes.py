__author__ = 'mh'

from network_stack import BasedApplicationLayer, BasedLayer, BasedPhyLayer, dot11pInterface
import world
from utils import Position
from applications.BasedApplication import BasedApplication
from network_elements.network_stack import IPv6Stack
from interfaces import Dot11pInterface
from world import *
from layers import NetworkLayer


class Inerface(object):
    def __init__(self, phy, mac):
        self.mac = mac
        self.phy = phy

class BasedNetworkLayer(BasedLayer):
    def __init__(self):
        super(BasedNetworkLayer, self).__init__()
        self.routing_table = None

class Router(object):
    def __init__(self):
        pass

class IPv6RouterStack(object):
    def __init__(self, env):
        self.env = env
        self.phy = BasedPhyLayer("PHY")
        self.mac = BasedLayer("MAC")
        self.network = BasedLayer("NETWORK")
        self.app = BasedApplicationLayer()

    def initialize(self, pipeline):
        self.phy.set_upper_layer(self.mac)
        self.mac.set_upper_layer(self.network)
        self.network.set_upper_layer(self.app)
        self.phy.set_aether(pipeline)

    def handle_received_msg(self, msg):
        self.phy.handle_lower_msg(msg)




class BasedNode(object):
    def __init__(self, name, x=0, y=0):
        self.env = world.env
        self.position = Position(x, y)
        self.name = name
        self.net_layer = NetworkLayer(self)
        self._last_update_time = self.env.now
        self._debug = DEBUG
        self.update_interval = world.update_interval
        self.app = BasedApplicationLayer() #BasedApplication(self.env, "OBU_APP_1", self.interface)
        self.app.active = False
        self.net_layer.set_upper_layer(self.app)
        env.process(self.app.run())


class RSU(BasedNode):
    def __init__(self, name, x=0, y=0):
        super(RSU, self).__init__(name, x, y)
        self.is_ap = True
        self.net_layer.it.add_interface_instance(dot11pInterface(self))
        #self.proc = self.env.process(self.run())

class OBU(BasedNode):
    def __init__(self, name, x=0, y=0, speed=50):
        super(OBU, self).__init__(name)
        self.speed = speed #[km/h]
        self.is_ap = False
        self.net_layer.it.add_interface_instance(dot11pInterface(self))
        self.proc = self.env.process(self.run())


    def run(self):
        while True:
            yield self.env.process(self.update())

    def update(self):
        self.update_position()
        self._last_update_time = self.env.now
        yield self.env.timeout(self.update_interval)

    def update_position(self):
        x, y = self.position.get()
        x += self.speed * 1000./3600 * (self.env.now - self._last_update_time)
        self.position.set(x,y)
        #print "{:<3s} position {:<10s} at {:4.5f}".format(self.name, self.position, env.now)
        #yield self.env.timeout(self.update_interval)



if __name__ == "__main__":
    obu = OBU("OBU1")
    rsu = RSU("RSU1")
    world.connection_manager.add_ap(rsu)
    world.connection_manager.add_node(obu)

    obu_11p_iface = obu.net_layer.it.get_interface_by_name('11p')
    obu_11p_iface.set_ipv6_address("2001::1", 64)
    obu_11p_iface.phy_layer.set_aether(world.bc_pipe)

    rsu_11p_iface = rsu.net_layer.it.get_interface_by_name('11p')
    rsu_11p_iface.set_ipv6_address("2001::1", 64)
    rsu_11p_iface.phy_layer.set_aether(world.bc_pipe)

    obu.net_layer.update_local_routes()
    rsu.net_layer.update_local_routes()
    obu.app.active = True

    world.env.run(until=1)