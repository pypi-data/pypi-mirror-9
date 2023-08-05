#----------------------------------------------------------------------------*/
# Copyright (c) FIRST 2008-2014. All Rights Reserved.                        */
# Open Source Software - may be modified and shared by FRC teams. The code   */
# must be accompanied by the FIRST BSD license file in the root directory of */
# the project.                                                               */
#----------------------------------------------------------------------------*/

import hal

from .analoginput import AnalogInput
from .livewindowsendable import LiveWindowSendable

__all__ = ["AnalogPotentiometer"]

class AnalogPotentiometer(LiveWindowSendable):
    """Reads a potentiometer via an :class:`.AnalogInput`
    
    Analog potentiometers read
    in an analog voltage that corresponds to a position. The position is in
    whichever units you choose, by way of the scaling and offset constants
    passed to the constructor.

    .. not_implemented: initPot
    """

    def __init__(self, channel, fullRange=1.0, offset=0.0):
        """AnalogPotentiometer constructor.

        Use the fullRange and offset values so that the output produces
        meaningful values. I.E: you have a 270 degree potentiometer and
        you want the output to be degrees with the halfway point as 0
        degrees. The fullRange value is 270.0(degrees) and the offset is
        -135.0 since the halfway point after scaling is 135 degrees.

        :param channel: The analog channel this potentiometer is plugged into.
        :type  channel: int or :class:`.AnalogInput`
        :param fullRange: The scaling to multiply the fraction by to get a
            meaningful unit.  Defaults to 1.0 if unspecified.
        :type  fullRange: float
        :param offset: The offset to add to the scaled value for controlling
            the zero value.  Defaults to 0.0 if unspecified.
        :type  offset: float
        """

        if not hasattr(channel, "getVoltage"):
            channel = AnalogInput(channel)
        self.analog_input = channel
        self.fullRange = fullRange
        self.offset = offset
        self.init_analog_input = True

    def get(self):
        """Get the current reading of the potentiometer.

        :returns: The current position of the potentiometer.
        :rtype: float
        """
        return (self.analog_input.getVoltage() / hal.getUserVoltage5V()) * self.fullRange + self.offset

    def pidGet(self):
        """Implement the PIDSource interface.

        :returns: The current reading.
        :rtype: float
        """
        return self.get()

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Analog Input"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("Value", self.get())

    def startLiveWindowMode(self):
        # don't have to do anything special when entering the LiveWindow
        pass

    def stopLiveWindowMode(self):
        # don't have to do anything special when exiting the LiveWindow
        pass

    def free(self):
        if self.init_analog_input:
            self.analog_input.free()
            del self.analog_input
            self.init_analog_input = False
