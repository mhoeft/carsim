__author__ = 'Michal Hoeft'

from addresses import MacAddress, IPv6Address
from tunnels import Tunnel
from network_stack import Interface

class InterfacesTable(object):
    def __init__(self):
        self.interfaces_table = {}

    def get_all_interfaces(self):
        return self.interfaces_table

    def add_interface_instance(self, interface_instance):
        self.interfaces_table[interface_instance.name] = interface_instance
        self.interfaces_table[interface_instance.name].mac_layer.upper_layer = interface_instance.owner.net_layer

    #def add_tunnel_interface(self):
    #    pass

    #def add_11p_interface(self):
    #    pass

    #def add_lte_interface(self):
    #    pass

    def get_interface_by_name(self, name):
        return self.interfaces_table[name]

    def get_interface_by_id(self, id):
        for interface in self.interfaces_table:
            if interface.id == id:
                return interface
        return None

if __name__ == "__main__":
    print MacAddress()
