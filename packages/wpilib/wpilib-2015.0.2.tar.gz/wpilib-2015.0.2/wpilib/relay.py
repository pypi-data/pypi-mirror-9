#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import weakref

from .livewindow import LiveWindow
from .resource import Resource
from .sensorbase import SensorBase

__all__ = ["Relay"]

def _freeRelay(port):
    hal.setRelayForward(port, False)
    hal.setRelayReverse(port, False)
    hal.freeDIO(port)

class Relay(SensorBase):
    """Controls VEX Robotics Spike style relay outputs.
    
    Relays are intended to be connected to Spikes or similar relays. The relay
    channels controls a pair of pins that are either both off, one on, the
    other on, or both on. This translates into two Spike outputs at 0v, one at
    12v and one at 0v, one at 0v and the other at 12v, or two Spike outputs at
    12V. This allows off, full forward, or full reverse control of motors without
    variable speed. It also allows the two channels (forward and reverse) to
    be used independently for something that does not care about voltage
    polarity (like a solenoid).
    
    .. not_implemented: initRelay
    """

    class Value:
        """The state to drive a Relay to."""
        
        #: Off
        kOff = 0
        
        #: On for relays with defined direction
        kOn = 1
        
        #: Forward
        kForward = 2
        
        #: Reverse
        kReverse = 3

    class Direction:
        """The Direction(s) that a relay is configured to operate in."""
        
        #: Both directions are valid
        kBoth = 0
        
        #: Only forward is valid
        kForward = 1
        
        #: Only reverse is valid
        kReverse = 2

    relayChannels = Resource(SensorBase.kRelayChannels * 2)

    def __init__(self, channel, direction=None):
        """Relay constructor given a channel.

        Initially the relay is set to both lines at 0v.

        :param channel: The channel number for this relay.
        :type  channel: int
        :param direction: The direction that the Relay object will control.
            If not specified, defaults to allowing both directions.
        :type  direction: :class:`Relay.Direction`
        """
        if direction is None:
            direction = self.Direction.kBoth
        self.channel = channel
        self.direction = direction

        self._initRelay()

        LiveWindow.addActuatorChannel("Relay", self.channel, self)
        self.set(self.Value.kOff)

    def _initRelay(self):
        SensorBase.checkRelayChannel(self.channel)
        try:
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kForward):
                Relay.relayChannels.allocate(self, self.channel * 2)
                hal.HALReport(hal.HALUsageReporting.kResourceType_Relay,
                              self.channel)
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kReverse):
                Relay.relayChannels.allocate(self, self.channel * 2 + 1)
                hal.HALReport(hal.HALUsageReporting.kResourceType_Relay,
                              self.channel + 128)
        except IndexError as e:
            raise IndexError("Relay channel %d is already allocated" % self.channel) from e

        self._port = hal.initializeDigitalPort(hal.getPort(self.channel))
        self._port_finalizer = weakref.finalize(self, _freeRelay, self._port)

    @property
    def port(self):
        if not self._port_finalizer.alive:
            return None
        return self._port

    def free(self):
        if (self.direction == self.Direction.kBoth or
            self.direction == self.Direction.kForward):
            Relay.relayChannels.free(self.channel*2)
        if (self.direction == self.Direction.kBoth or
            self.direction == self.Direction.kReverse):
            Relay.relayChannels.free(self.channel*2 + 1)

        self._port_finalizer()

    def set(self, value):
        """Set the relay state.

        Valid values depend on which directions of the relay are controlled by
        the object.

        When set to kBothDirections, the relay can be set to any of the four
        states: 0v-0v, 12v-0v, 0v-12v, 12v-12v

        When set to kForwardOnly or kReverseOnly, you can specify the constant
        for the direction or you can simply specify kOff and kOn. Using only
        kOff and kOn is recommended.

        :param value: The state to set the relay.
        :type  value: :class:`Relay.Value`
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        if value == self.Value.kOff:
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kForward):
                hal.setRelayForward(self.port, False)
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kReverse):
                hal.setRelayReverse(self.port, False)
        elif value == self.Value.kOn:
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kForward):
                hal.setRelayForward(self.port, True)
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kReverse):
                hal.setRelayReverse(self.port, True)
        elif value == self.Value.kForward:
            if self.direction == self.Direction.kReverse:
                raise ValueError("A relay configured for reverse cannot be set to forward")
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kForward):
                hal.setRelayForward(self.port, True)
            if self.direction == self.Direction.kBoth:
                hal.setRelayReverse(self.port, False)
        elif value == self.Value.kReverse:
            if self.direction == self.Direction.kForward:
                raise ValueError("A relay configured for forward cannot be set to reverse")
            if self.direction == self.Direction.kBoth:
                hal.setRelayForward(self.port, False)
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kReverse):
                hal.setRelayReverse(self.port, True)
        else:
            raise ValueError("Invalid value argument '%s'" % value)

    def get(self):
        """Get the Relay State

        Gets the current state of the relay.

        When set to kForwardOnly or kReverseOnly, value is returned as kOn/kOff
        not kForward/kReverse (per the recommendation in Set)

        :returns: The current state of the relay
        :rtype: :class:`Relay.Value`
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        if hal.getRelayForward(self.port):
            if hal.getRelayReverse(self.port):
                return self.Value.kOn
            else:
                if self.direction == self.Direction.kForward:
                    return self.Value.kOn
                else:
                    return self.Value.kForward
        else:
            if hal.getRelayReverse(self.port):
                if self.direction == self.Direction.kReverse:
                    return self.Value.kOn
                else:
                    return self.Value.kReverse
            else:
                return self.Value.kOff

    def setDirection(self, direction):
        """Set the Relay Direction.

        Changes which values the relay can be set to depending on which
        direction is used.

        Valid inputs are kBothDirections, kForwardOnly, and kReverseOnly.

        :param direction: The direction for the relay to operate in
        :type  direction: :class:`Relay.Direction`
        """
        if self.direction == direction:
            return
        
        if direction not in [self.Direction.kBoth,
                             self.Direction.kForward,
                             self.Direction.kReverse]:
            raise ValueError("Invalid direction argument '%s'" % direction)

        self.free()
        self.direction = direction
        self._initRelay()

    # Live Window code, only does anything if live window is activated.
    def getSmartDashboardType(self):
        return "Relay"

    def updateTable(self):
        table = self.getTable()
        if table is None:
            return
        v = self.get()
        if v == self.Value.kOn:
            table.putString("Value", "On")
        elif v == self.Value.kForward:
            table.putString("Value", "Forward")
        elif v == self.Value.kReverse:
            table.putString("Value", "Reverse")
        else:
            table.putString("Value", "Off")

    def valueChanged(self, itable, key, value, bln):
        if value == "Off":
            self.set(self.Value.kOff)
        elif value == "On":
            self.set(self.Value.kOn)
        elif value == "Forward":
            self.set(self.Value.kForward)
        elif value == "Reverse":
            self.set(self.Value.kReverse)
