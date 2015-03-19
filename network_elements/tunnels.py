__author__ = 'Michal Hoeft'

class Tunnel(object):
    def __init__(self, local, remote, interface):
        self.name = "InterfaceName"
        self.id = id
        self.local = local
        self.remote = remote
        self.interface = interface
        self.ipv6_address = None
        self._HEADER_SIZE = 40

    def set_ipv6_address(self, ipv6):
        self.ipv6_address = ipv6


if __name__ == "__main__":
    tun = Tunnel("local","remote","eth")

