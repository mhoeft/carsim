__author__ = 'Michal Hoeft'


from network_stack import BasedLayer
from routing_table import RoutingTable
from interfaces_table import InterfacesTable
from world import *
from msgs.BasedMessage import IPv6Datagram

class NetworkLayer(BasedLayer):
    def __init__(self, owner):
        self.is_router = False
        self.rt = RoutingTable()
        self.it = InterfacesTable()
        self.owner = owner


    def update_local_routes(self):
        list_of_interfaces = self.it.get_all_interfaces().values()
        for iface in list_of_interfaces:
            ipv6_address = iface.get_ipv6_address()
            self.rt.add_route(ipv6_address.network, None, iface.name)


    def get_ipv6(self):
        list_of_interfaces = self.it.get_all_interfaces().values()
        ipv6_address = None
        while ipv6_address == None and len(list_of_interfaces)>0:
            iface = list_of_interfaces.pop()
            ipv6_address = iface.get_ipv6_address()
        return ipv6_address


    def handle_upper_msg(self, msg):
        dst_node = connection_manager.get_element_by_name(msg.dst)
        dst_ipv6_address = dst_node.net_layer.get_ipv6()
        route = self.rt.get_route(dst_ipv6_address)
        out_interface = self.it.get_interface_by_name(route.interface)
        src_ipv6_address = out_interface.ipv6_address
        ipv6_msg = IPv6Datagram(src_ipv6_address, dst_ipv6_address,msg)
        out_interface.handle_upper_msg(ipv6_msg)

    def handle_lower_msg(self, msg):
        # act as a router
        if self.is_router:
            pass
        # otherwise it is client
        else:
            print "rcv message from %s" % msg.dst_address
            msg = msg.payload
            self.upper_layer.handle_lower_msg(msg)