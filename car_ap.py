__author__ = 'Michal Hoeft'
import simpy
import time
from utils import Position
from network_elements import RSU, OBU
from world import ConnectionManager
from utils import TimeLogger
import random

env = simpy.Environment()
c_mng = ConnectionManager(env)

car1 = OBU(env, "Car1", 10)
car1.position.set(0, 0)
car1._debug = False
car1.app.active = False

car2 = OBU(env, "Car2", 50)
car2.position.set(500, 3)
car2.app.active = False
car2._debug = False

car3 = OBU(env, "Car3", 70)
car3.position.set(100, 2)
car3.app.active = False
car3._debug = False

car4 = OBU(env, "Car4", 65)
car4.position.set(100, 1)
car4.app.active = False
car4._debug = False

ap1 = RSU(env, "RSU1")
ap1.position.set(0, 0.000001)
#ap1.app.active = True

c_mng.add_ap(ap1)
c_mng.add_node(car1)
c_mng.add_node(car2)
c_mng.add_node(car3)
c_mng.add_node(car4)

time_logger = TimeLogger(env)
# start processes
start_time = time_logger.set_start_time()
print "Starting simulation"
env.run(until=10000)
print "Simulation done in %f s" % (time.time()-start_time)

#print ap1.interface.print_report()
print car1.interface.print_report()
#print car2.interface.print_report()
#print car3.interface.print_report()
#print car4.interface.print_report()


from pylab import *
nodes = {}
#nodes["car1"] = car1
nodes["car2"] = car2
nodes["car3"] = car3
#nodes["car4"] = car4

t_tables = {}
d_tables = {}

for key in nodes.keys():
    t_tables[key] = []
    d_tables[key] = []
    for d in nodes[key].interface.bandwidth:
        t_tables[key].append(d["time"])
        d_tables[key].append(d["data"])
    plot(t_tables[key], d_tables[key], "o", label=key)
xlabel('sim. time (s)')
ylabel('received data [bits]')
grid(True)
legend(loc=2)
show()
