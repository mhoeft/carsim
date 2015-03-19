__author__ = 'mh'


from network_elements.addresses import IPv6Address, MacAddress
import world

class BasedMessage(object):
    def __init__(self, env):
        self.env = env
        #self.payload = None

    def __str__(self):
        return self.msg #.print_payload(self)

    def print_payload(self, msg):
        if hasattr(msg, 'payload'):
            return "msg %s\n" % msg.payload
            self.print_payload(msg.payload)
        else:
            return "msg %s\n" % msg

class EthernetFrame(BasedMessage):
    def __init__(self, src, dst, msg):
        super(EthernetFrame,self).__init__(msg.env)
        self.mac_dst = dst
        self.mac_src = src
        self.tag1q = None
        self.ethertype = None
        self.payload = msg
        self._header_size = 18*8
        self._mtu = 1500

    @classmethod
    def to_node(self, src, dst, msg):
        return EthernetFrame(src.mac, dst.mac, msg)

class IPv6Datagram(BasedMessage):
    def __init__(self, src, dst, msg):
        super(IPv6Datagram,self).__init__(msg.env)
        self.version = "6"
        self.traffic_class = None
        self.flow_label = None
        self.next_header = None
        self.hop_limit = None
        self.src_address = src
        self.dst_address = dst
        self.payload_length = None
        self.payload = msg
        self._header_size = 40*8

class UDP(BasedMessage):
    def __init__(self, sport, dport, msg, env = None):
        if env:
            self.env = env
        else:
            super(UDP,self).__init__(msg.env)
        self.sport = sport
        self.dport = dport
        self.payload = msg


class AppMsg(BasedMessage):
    def __init__(self, dst_name, msg):
        self.env = world.env
        self.dst = dst_name
        self.msg = msg


if __name__ == "__main__":
    print "TEST"
    import simpy
    msg = "TEST"
    env = simpy.Environment()
    udp = UDP(80, 80, msg, env=env)
    ipv6 = IPv6Datagram("2001:db8::", "2000:db8::", udp)
    src = MacAddress()
    dst = MacAddress()
    ether = EthernetFrame(src, dst, ipv6)

    print ether