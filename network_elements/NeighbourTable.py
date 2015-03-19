__author__ = 'Michal Hoeft'


class NeighbourInstance(object):
    def __init__(self, ipv6, mac):
        self.ipv6 = ipv6
        self.mac = mac


class NeighbourTable(object):
    def __init__(self):
        self.nt_by_ipv6 = {}
        self.nt_by_mac = {}

    def add_instance(self, instance):
        self.nt_by_ipv6[instance.ipv6] = instance
        self.nt_by_mac[instance.mac] = instance

    def get_mac(self, ipv6):
        return self.nt_by_ipv6[ipv6]

    def get_ipv6(self, mac):
        return self.nt_by_mac[mac]