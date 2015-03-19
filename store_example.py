__author__ = 'mh'

"""
Animal location example

Covers:

- Event propagation
- Process interconnects

Scenario:
  A set of transmitters on poles around an animal compound periodically send out
  time stamped messages.  A set of electronic collars on the animals receive these
  messages and from them determine their position through triangulation.
  There is also a game keeper inside the animal compound with a locator.
  They all  transmit their location to the animal control center

"""
import random

import simpy
from collections import namedtuple

txMsg = namedtuple('txMsg', 'name, time, location')
triData = namedtuple('triData', 'time, location, r')

# Assume: time in seconds and distances in meters
SPEED_OF_LIGHT = 299792458.0 # m/s
COMPOUNDSIZE = [50, 50] # +- x and y size of animal compound

class Aether:
    ''' Aether represents free space and calculates the propagation delay of events between two locations '''
    def __init__(self, env):
        self.env = env
        self.receivers = []

    def addReceiver(self, aReceiver):
        self.receivers.append(aReceiver)


    # propagate is started as a process every time an event (in this case a msg) needs time to travel between
    # two processes.  propagate encapsulates the delay mechanism outside of the two processes that send and receive
    # the message.  This approach can be used for any model element which delays an event (propagation through space,
    # cables, device latency) and can also be used to schedule future events sent to another process without delaying
    # the sending process.   simpy.resources.Store is used and an event pipe that buffers the messages
    def propagate(self, sourceLoc, destLoc, destConn, payload, velocity=SPEED_OF_LIGHT):
            propDelay = (((destLoc[0] - sourceLoc[0])**2 + (destLoc[1] - sourceLoc[1])**2  )**0.5) / velocity
            yield self.env.timeout(propDelay)
            destConn.put(payload)

    def transmission(self, emitter, msg):
        #print('Emitter {} Transmitting at time {}'.format(emitter.name, self.env.now))

        for aReceiver in self.receivers:
            if aReceiver.listeningFor(emitter):
                self.env.start(self.propagate( emitter.xyLocation, aReceiver.xyLocation, aReceiver.inPipe, msg))



class BroadcastPipe(object):
    def __init__(self,  env, capacity=simpy.core.Infinity, item_q_type=simpy.resources.queues.FIFO,
                 event_type=simpy.resources.events.StoreEvent):
        self.rcvrs = []

        self.env = env
        self.capacity = capacity
        self.item_q_type = item_q_type
        self.event_type = event_type

    def put(self, value):
        events = []
        for store in self.rcvrs:
            events.append(store.put(value))

        return simpy.core.Condition(self.env, simpy.core.all_events, events)

    def getOutputConn(self, capacity=None,
                  item_q_type=None,
                  event_type=None):

        if  capacity == None:
            capacity = self.capacity
        if  item_q_type == None:
            item_q_type = self.item_q_type
        if  event_type == None:
            event_type  =self.event_type

        aPipe = simpy.resources.Store(self.env,
                                      capacity=capacity,
                                      item_q_type=item_q_type,
                                      event_type=event_type)
        self.rcvrs.append(aPipe)
        return aPipe



class Transmitter(object):
    '''
    A transmitter on a pole that broadcasts periodic
    time stamped messages
    '''

    def __init__(self, env, name, txPeriod, xyLocation, aether):
        self.env = env
        self.name = name
        self.txPeriod = txPeriod
        self.xyLocation = xyLocation
        self.aether = aether
        self.env.start(self.transmit())

    def transmit(self):
        while(True):
            # wait for next transmission
            yield self.env.timeout(self.txPeriod)

            msg = txMsg(self.name, self.env.now, self.xyLocation)
            self.aether.transmission( self, msg)



class Locator(object):
    '''
    A transmitter on a pole that broadcasts periodic
    time stamped messages
    '''

    def __init__(self, env, name, xyzLocation, inPipe, aether, transmitters):
        self.env = env
        self.name = name
        self.xyLocation = xyzLocation
        self.inPipe = inPipe
        self.aether = aether
        self.txes = {akey:None for akey in transmitters}
        self.env.start(self.Process())

    def listeningFor(self, source):
        if isinstance(source, Transmitter):
            return True
        else:
            return False

    def Process(self):
        while(True):
            # wait for next transmission
            msg = yield self.inPipe.get()

            # Update the transmitter range data
            self.txes[msg.name] = triData( msg.time, msg.location, (self.env.now - msg.time) * SPEED_OF_LIGHT)

            #===================================================================
            # Calculate location
            #===================================================================
            x = []
            y = []
            r = []
            for aTx in self.txes:
                if self.txes[aTx] is None:
                    break
                x.append(self.txes[aTx].location[0])
                y.append(self.txes[aTx].location[1])
                r.append(self.txes[aTx].r)
            else:
                # using the latest transmitter range and position data, calculate the current location
                myX = ((((r[0]**2 - r[1]**2) + (x[1]**2 - x[0]**2) + (y[1]**2 - y[0]**2) ) * (2.0 *y[2] - 2.0 * y[1])
                       - ((r[1]**2 - r[2]**2) + (x[2]**2 - x[1]**2) + (y[2]**2 - y[1]**2) ) * (2.0 *y[1] - 2.0 * y[0]))
                       / ((2.0*x[1] - 2.0*x[2]) * (2.0*y[1] - 2.0*y[0]) - (2.0*x[0] - 2.0*x[1]) * (2.0*y[2] - 2.0*y[1])))

                myY = ((r[0]**2 - r[1]**2)+ (x[1]**2 - x[0]**2) + (y[1]**2 - y[0]**2) + myX * (2.0*x[0] - 2.0*x[1])) / (2.0*y[1] - 2.0*y[0])

                # create a message and broadcast it into space
                msg = txMsg(self.name, self.env.now, [myX, myY])
                self.aether.transmission( self, msg)

            #===================================================================
            # Move about
            #===================================================================
            dx, dy = random.choice([(0,1), (0, -1), (1,0), (-1,0)])

            # Update position:
            self.xyLocation[0] = self.xyLocation[0] + dx
            self.xyLocation[1] = self.xyLocation[1] + dy

            # Limit movement to within compound
            if self.xyLocation[0] > COMPOUNDSIZE[0]:
                self.xyLocation[0] = COMPOUNDSIZE[0]
            elif self.xyLocation[0] < -COMPOUNDSIZE[0]:
                self.xyLocation[0] = -COMPOUNDSIZE[0]

            if self.xyLocation[1] > COMPOUNDSIZE[1]:
                self.xyLocation[1] = COMPOUNDSIZE[1]
            elif self.xyLocation[1] < -COMPOUNDSIZE[1]:
                self.xyLocation[1] = -COMPOUNDSIZE[1]



class ControlCenter(object):
    '''
    A transmitter on a pole that broadcasts periodic
    time stamped messages
    '''

    def __init__(self, env, name, xyLocation, inPipe, outPipe, keeper):
        self.env = env
        self.name = name
        self.xyLocation = xyLocation
        self.inPipe = inPipe
        self.outPipe = outPipe
        self.keeperName = keeper.name
        self.env.start(self.monitor())

    def listeningFor(self, source):
        if isinstance(source, Locator):
            return True
        else:
            return False

    def monitor(self):
        keeperLocation = [100, 100]
        while(True):
            # wait for next transmission
            msg = yield self.inPipe.get()
            print('At time {:.1f},  {} is located at x={:.1f} and y={:.1f} '.format(msg.time, msg.name, msg.location[0], msg.location[1]))
            if msg.name ==  self.keeperName:
                keeperLocation = msg.location
            else:
                if ((keeperLocation[0] - msg.location[0])**2 + (keeperLocation[1] - msg.location[1])**2) < 9.0:  # if an animal is within 3 m then he pounces on keeper
                    print('\nOH MY GOD!, The {} is eating {}!\n'.format(msg.name, self.keeperName))
                    self.outPipe.put(self.keeperName)
                    raise Exception('{} is dead'.format(self.keeperName))


def toBeNotified(name, response, inPipe):
    msg = yield inPipe.get()
    print('{}: {}'.format(name, response.format(msg)))


duration = 1000

env = simpy.Environment()
space = Aether(env)

# for trilateration we will need three transmitters
txNames = ['Tx A','Tx B','Tx C' ]
txA = Transmitter(env=env, name=txNames[0], txPeriod=1.0, xyLocation=[100, 0], aether=space)
txB = Transmitter(env=env, name=txNames[1], txPeriod=1.1, xyLocation=[0, 100], aether=space)
txC = Transmitter(env=env, name=txNames[2], txPeriod=1.4, xyLocation=[100, 200], aether=space)

# Here a number of pipes are created and used to interconnect different processes
# a simpy Store resource works great as a one-to-one or many-to-one pipe
pipe1 = simpy.resources.Store(env)
pipe2 = simpy.resources.Store(env)
pipe3 = simpy.resources.Store(env)
pipe4 = simpy.resources.Store(env)
pipe5 = simpy.resources.Store(env)
pipe6 = simpy.resources.Store(env)

# For one-to-many (especially where streaming events are consumed at different rates). A Broadcast pipe
# mechanism is used (see code above for BroadcastPipe class)
notifyPipe = BroadcastPipe(env)

listeners = []

listeners.append(Locator(env=env, name='Lion',  xyzLocation=[0,0], inPipe=pipe1, aether=space, transmitters=txNames))
listeners.append(Locator(env=env, name='Tiger', xyzLocation=[0,0], inPipe=pipe2, aether=space, transmitters=txNames))
listeners.append(Locator(env=env, name='Bear',  xyzLocation=[0,0], inPipe=pipe3, aether=space, transmitters=txNames))
listeners.append(Locator(env=env, name='Rhino', xyzLocation=[0,0], inPipe=pipe4, aether=space, transmitters=txNames))

listeners.append(Locator(env=env, name='Karl', xyzLocation=[20,20], inPipe=pipe5, aether=space, transmitters=txNames))

listeners.append(ControlCenter(env=env, name='headQuarters', xyLocation=[1000, 1000], inPipe=pipe6, outPipe=notifyPipe, keeper=listeners[-1]))

for aListener in listeners:
    space.addReceiver(aListener)

env.start(toBeNotified(name='Emergency', response= 'Ambulance Dispatched to save {}', inPipe=notifyPipe.getOutputConn()))
env.start(toBeNotified(name='Animal Control', response= "I'm on my way to tranquilize the animal eating {}", inPipe=notifyPipe.getOutputConn()))
env.start(toBeNotified(name='Wife', response= 'Poor {}, now where are those life insurance papers?', inPipe=notifyPipe.getOutputConn()))

simpy.simulate(env, until=duration)
