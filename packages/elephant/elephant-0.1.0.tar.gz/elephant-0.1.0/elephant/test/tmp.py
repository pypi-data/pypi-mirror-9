from __future__ import division
import numpy
from scipy.stats import kstest
from quantities import ms, Hz

import elephant.spike_train_generation as stgen
from elephant.statistics import isi


def pdiff(a, b):
    """Difference between a and b as a fraction of a

    i.e. abs((a - b)/a)
    """
    return abs((a - b)/a)
    #return (a - b)/a


a = 3.0
b = 67.0*Hz
rate = b/a
#rate = 123.0*Hz
t_stop = 2345*ms

N = 10000

esc = numpy.empty((N,))
emi = numpy.empty((N,))
efs = numpy.empty((N,))
els = numpy.empty((N,))
D = numpy.empty((N,))
p = numpy.empty((N,))

for i in range(N):
    #spiketrain = stgen.homogeneous_poisson_process(rate, t_stop=t_stop)
    spiketrain = stgen.homogeneous_gamma_process(a, b, t_stop=t_stop)
    #print spiketrain[0],
    intervals = isi(spiketrain)

    expected_spike_count = int((rate * t_stop).simplified)
    esc[i] = pdiff(expected_spike_count, spiketrain.size)

    expected_mean_isi = (1/rate).rescale(ms)
    emi[i] = pdiff(expected_mean_isi, intervals.mean())

    expected_first_spike = 0*ms
    efs[i] = (spiketrain[0] - expected_first_spike)/expected_mean_isi

    expected_last_spike = t_stop
    els[i] = (expected_last_spike - spiketrain[-1])/expected_mean_isi

    # Kolmogorov-Smirnov test
    D[i], p[i] = kstest(intervals,
                        #"expon", args=(0, expected_mean_isi),  # args are (loc, scale)
                        "gamma", args=(a, 0.0, (1/b).rescale(t_stop.units)),  # args are (a, loc, scale)
                        alternative='two-sided')

esc.sort()
emi.sort()
efs.sort()
els.sort()
D.sort()
p.sort()

for x in (esc, emi, efs, els, D, p[::-1]):
    print x[int(0.99*x.size)], x[int(0.999*x.size)]

