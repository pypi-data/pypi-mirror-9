#!/usr/bin/python

from pycomedi.device import Device
from pycomedi.channel import AnalogChannel
from pycomedi.constant import SUBDEVICE_TYPE, AREF, UNIT

import numpy
from pylab import *


class Tester (object):
    def __init__(self):
        self.device = Device('/dev/comedi0')
        self.device.open()
        self.ai_subdevice = self.device.find_subdevice_by_type(
            SUBDEVICE_TYPE.ai)
        self.ao_subdevice = self.device.find_subdevice_by_type(
            SUBDEVICE_TYPE.ao)
        self.ai_channels = [
            self.ai_subdevice.channel(i, factory=AnalogChannel, aref=AREF.diff)
            for i in (0, 1)]
        self.ao_channels = [
            self.ao_subdevice.channel(i, factory=AnalogChannel, aref=AREF.diff)
            for i in (0, 1)]
        for chan in self.ai_channels + self.ao_channels:
            chan.range = chan.find_range(unit=UNIT.volt, min=-10, max=10)
        self.ai_converters = [c.get_converter() for c in self.ai_channels]
        self.ao_converters = [c.get_converter() for c in self.ao_channels]

    def close(self):
        self.device.close()
        self.device = None

    def read(self):
        return [cv.to_physical(cn.data_read_delayed(nano_sec=1e3))
                for cv,cn in zip(self.ai_converters, self.ai_channels)]

    def write(self, values):
        for i,v in enumerate(values):
            self.ao_channels[i].data_write(
                self.ao_converters[i].from_physical(v))

    def run(self):
        ao_maxdata = self.ao_channels[0].get_maxdata()
        ao_min = -5
        ao_max = 5
        points = int(1e3)
        ao_data = numpy.concatenate((
                numpy.linspace(0, ao_max, points/2),
                numpy.linspace(ao_max, ao_min, points),
                numpy.linspace(ao_min, 0, points/2)))
        ai_data = []
        for i,v in enumerate(ao_data):
            self.write([v, -v])
            ai_data.append(self.read())
        self.write([0, 0])
        ai_data = numpy.array(ai_data)
        self.plot(ao_data, ai_data)

    def plot(self, ao_data, ai_data):
        print(ao_data.shape)
        print(ai_data.shape)
        subplot(3,2,1)
        plot(ao_data, 'r.')
        subplot(3,2,3)
        plot(ai_data[:,0], 'b.')
        subplot(3,2,5)
        plot(ai_data[:,1], 'g.')
        subplot(1,2,2)
        plot(ao_data, ai_data[:,0], 'r.')
        show()


if __name__ == '__main__':
    t = Tester()
    t.run()
    t.close()
