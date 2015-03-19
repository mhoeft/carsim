__author__ = 'mh'

import math
import time

class TimeLogger():
    def __init__(self,env):
        self.env = env
        self.proc = env.process(self.run())
        self.start_time = time.time()

    def run(self):
        while True:
            yield self.env.process(self.log_time())

    def log_time(self):
        print "Simulation time {:4.5f} after {:4.5f}s".format(self.env.now, time.time()-self.start_time)
        yield self.env.timeout(180)

    def set_start_time(self):
        self.start_time = time.time()
        return self.start_time

class Position(object):
    def __init__(self, x = 0, y = 0):
        self.x = float(x)
        self.y = float(y)

    def set(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def get(self):
        return [self.x, self.y]

    def calculate_distance(self, obj):
        return math.sqrt((self.x - obj.position.x)**2 + (self.y - obj.position.y)**2)

    def __str__(self):
        return "x=%f, y=%f" % (self.x, self.y)