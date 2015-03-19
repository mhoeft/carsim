__author__ = 'Michal Hoeft'

from IPy import IP
from random import randint

class IPv6Address(object):
    """ IPv6Address Class
    """
    def __init__(self, address, netmask=64):
        """Class IPv6Address.

            Args:
               address (str): string containing IPv6 address
               netmask(str): netmast length
        """
        self.address = IP(address)
        self.network = self.address.make_net(netmask)

    def __str__(self):
        return self.address.strNormal()

class MacAddress(object):
    def __init__(self, mac=None):
        if mac:
            self.mac = str(mac).lower()
        else:
            self.mac = MacAddress.generate_random_mac()

    def __str__(self):
        return "%s" % self.mac

    @staticmethod
    def generate_random_mac():
        hex_table = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]
        mac = ""
        for i in xrange(12):
            mac += hex_table[randint(0,15)]
            if (i)%2 and i<11:
                mac += ":"
        mac = str(mac)
        return mac