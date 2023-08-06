__author__ = 'andrew'


import math
import numpy as np
from neo import AnalogSignalArray, SpikeTrain
from quantities import ms
from elephant.sta import spike_triggered_average

s = AnalogSignalArray(np.array([np.sin(np.arange(0, 20*math.pi, 0.1))]).T, units='mV', sampling_rate=10/ms)

print "======= 1 ======="
st1 = SpikeTrain([9*math.pi, 10*math.pi, 11*math.pi, 12*math.pi], units= 'ms', t_stop= s.t_stop)
sta1 = spike_triggered_average(s, st1, (0*ms, 5*ms))
print sta1.max()

print "======= 2 ======="
st2 = SpikeTrain([9*math.pi, 10*math.pi, 11*math.pi, 12*math.pi], units= 'ms', t_stop= 13*math.pi)
sta2 = spike_triggered_average(s, st2, (0*ms, 5*ms))
print sta2.max()
