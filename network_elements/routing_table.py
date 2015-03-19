__author__ = 'mh'

from IPy import IP
from addresses import IPv6Address

class Route(object):
    def __init__(self, network, gateway, interface=None, priority=20, familiy="INET6"):
        self.interface = interface
        self.network = IP(network)
        self.gateway = gateway
        self.priority = priority
        self.familiy = familiy

    def __str__(self):
        return "%s via %s iface %s" % (self.network, self.gateway, self.interface)


class RoutingTable(object):
    def __init__(self):
        self.routing_table = {}

    def add_route(self, network, gateway, interface=None, priority=20):
        route = Route(network, gateway, interface=interface, priority=priority)
        self.routing_table[route.network] = route

    def get_default_gateway(self):
        default = IP("::/0")
        gw = self.routing_table[default]
        return gw

    def get_route(self, host):
        if isinstance(host, IPv6Address):
            host = host.address
        else:
            host = IP(host)
        available_routes = [route for route in self.routing_table.keys() if host in route]
        best_route_key = sorted(available_routes, key=lambda x: x._prefixlen)[-1]
        return self.routing_table[best_route_key]


if __name__ == "__main__":
    print "TEST"
    rt = RoutingTable()
    rt.add_route("2000:db8::/64", "2000:db8::ff")
    rt.add_route("2000:db8::/32", "2000:db8::aa")
    rt.add_route("::/0", "1::1")
    print "Routing table"
    print rt.routing_table
    print "Default GW"
    print rt.get_default_gateway()
    print "get_route"
    print rt.get_route("3000:db8::1")