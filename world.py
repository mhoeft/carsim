__author__ = 'Michal Hoeft'

import simpy
from network_elements.WirelessPipe import BroadcastPipe

DEBUG = True
neighbour_table ={}
env = simpy.Environment()
update_interval = 0.1
bc_pipe = BroadcastPipe(env)


class BasedConnection(object):
    def __init__(self, connection_manager, obj1, obj2):
        self.obj1 = obj1
        self.obj2 = obj2
        self.env = obj2.env
        self.type = "Based"
        self.connection_manager = connection_manager
        self.store = simpy.Store(self.env)

    def latency(self, msg):
        yield self.env.timeout(0.01)
        self.connection_manager.get(msg)
        #self.store.put(msg)

    def put(self, msg):
        self.env.process(self.latency(msg))

    def get(self):
        return self.store.get()

class ConnectionManager(object):
    def __init__(self):
        self.env = env
        self.ap_list = []
        self.node_list = []
        self.connection_list = []
        self.object_list = {}

    def put(self, msg):
        connection_list = self.get_object_connection(msg._source)
        if len(connection_list):
            connection = connection_list[0]
            connection.put(msg)
            #self.env.process(self.latency(msg))

    def get(self, msg):
        for ap in self.ap_list:
            ap.interface.receive(msg)
        for node in self.node_list:
            node.interface.receive(msg)

    def add_node(self, node):
        self.node_list.append(node)
        #node.interface.connection_manager = self
        self.object_list[node.name] = node

    def add_ap(self, ap):
        self.ap_list.append(ap)
        #ap.interface.connection_manager = self
        self.object_list[ap.name] = ap

    def get_element_by_name(self, name):
        return self.object_list[name]




    def update_connection(self):
        for ap in self.ap_list:
            for node in self.node_list:
                distance = ap.position.calculate_distance(node)
                if distance < 10000:
                    connection = self.get_connection_between_object(node, ap)
                    if not connection:
                        self.connection_list.append(BasedConnection(self, node, ap))
                        if node._debug:
                            print "\t\t %s connecting to %s at %f" % (node.name, ap.name, self.env.now)
                    if node._debug:
                        print "%s in range of %s" % (node.name, ap.name)
                        print "%s position %s at %f" % (node.name, node.position, self.env.now)
                else:
                    connection = self.get_connection_between_object(node, ap)
                    if connection:
                        #del connection
                        index = self.connection_list.index(connection)
                        del self.connection_list[index]
                        if node._debug:
                            print "\t\t %s diconecting to %s at %f" % (node.name, ap.name, self.env.now)
                            print "\t\t%s position %s at %f" % (node.name, node.position, self.env.now)

    def get_object_connection(self, obj):
        result_list = []
        result_list = []
        for connection in self.connection_list:
            if connection.obj1 == obj or connection.obj2 == obj:
                result_list.append(connection)
        return result_list

    def delete_connection_between_object(self, obj1, obj2):
        for connection in self.connection_list:
            if (connection.obj1 == obj1 and connection.obj2 == obj2) or (connection.obj1 == obj2 and connection.obj2 == obj1):
                return connection
        return None

    def get_connection_between_object(self, obj1, obj2):
        for connection in self.connection_list:
            if (connection.obj1 == obj1 and connection.obj2 == obj2) or (connection.obj1 == obj2 and connection.obj2 == obj1):
                return connection
        return None

connection_manager = ConnectionManager()