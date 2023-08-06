# -*- coding: utf-8 -*-
"""
Statistical measures of spike trains (e.g., Fano factor) and functions to estimate firing rates.

:copyright: Copyright 2014-2015 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""

from __future__ import division, print_function

import numpy as np
import quantities as pq
import scipy.stats
import scipy.signal
import neo
import warnings
import elephant.conversion as conv


def isi(spiketrain, axis=-1):
    """
    Return an array containing the inter-spike intervals of the SpikeTrain.

    Accepts a Neo SpikeTrain, a Quantity array, or a plain NumPy array.
    If either a SpikeTrain or Quantity array is provided, the return value will
    be a quantities array, otherwise a plain NumPy array. The units of
    the quantities array will be the same as spiketrain.

    Parameters
    ----------

    spiketrain : Neo SpikeTrain or Quantity array or NumPy ndarray
                 The spike times.
    axis : int, optional
           The axis along which the difference is taken.
           Default is the last axis.

    Returns
    -------

    NumPy array or quantities array.

    """
    if axis is None:
        axis = -1
    intervals = np.diff(spiketrain, axis=axis)
    if hasattr(spiketrain, 'waveforms'):
        intervals = pq.Quantity(intervals.magnitude, units=spiketrain.units)
    return intervals


def mean_firing_rate(spiketrain, t_start=None, t_stop=None, axis=None):
    """
    Return the firing rate of the SpikeTrain.

    Accepts a Neo SpikeTrain, a Quantity array, or a plain NumPy array.
    If either a SpikeTrain or Quantity array is provided, the return value will
    be a quantities array, otherwise a plain NumPy array. The units of
    the quantities array will be the inverse of the spiketrain.

    The interval over which the firing rate is calculated can be optionally
    controlled with `t_start` and `t_stop`

    Parameters
    ----------

    spiketrain : Neo SpikeTrain or Quantity array or NumPy ndarray
                 The spike times.
    t_start : float or Quantity scalar, optional
              The start time to use for the interval.
              If not specified, retrieved from the``t_start`
              attribute of `spiketrain`.  If that is not present, default to
              `0`.  Any value from `spiketrain` below this value is ignored.
    t_stop : float or Quantity scalar, optional
             The stop time to use for the time points.
             If not specified, retrieved from the `t_stop`
             attribute of `spiketrain`.  If that is not present, default to
             the maximum value of `spiketrain`.  Any value from
             `spiketrain` above this value is ignored.
    axis : int, optional
           The axis over which to do the calculation.
           Default is `None`, do the calculation over the flattened array.

    Returns
    -------

    float, quantities scalar, NumPy array or quantities array.

    Notes
    -----

    If `spiketrain` is a Quantity or Neo SpikeTrain and `t_start` or `t_stop`
    are not, `t_start` and `t_stop` are assumed to have the same units as
    `spiketrain`.

    Raises
    ------

    TypeError
        If `spiketrain` is a NumPy array and `t_start` or `t_stop`
        is a quantity scalar.

    """
    if t_start is None:
        t_start = getattr(spiketrain, 't_start', 0)

    found_t_start = False
    if t_stop is None:
        if hasattr(spiketrain, 't_stop'):
            t_stop = spiketrain.t_stop
        else:
            t_stop = np.max(spiketrain, axis=axis)
            found_t_start = True

    # figure out what units, if any, we are dealing with
    if hasattr(spiketrain, 'units'):
        units = spiketrain.units
    else:
        units = None

    # convert everything to the same units
    if hasattr(t_start, 'units'):
        if units is None:
            raise TypeError('t_start cannot be a Quantity if '
                            'spiketrain is not a quantity')
        t_start = t_start.rescale(units)
    elif units is not None:
        t_start = pq.Quantity(t_start, units=units)
    if hasattr(t_stop, 'units'):
        if units is None:
            raise TypeError('t_stop cannot be a Quantity if '
                            'spiketrain is not a quantity')
        t_stop = t_stop.rescale(units)
    elif units is not None:
        t_stop = pq.Quantity(t_stop, units=units)

    if not axis or not found_t_start:
        return np.sum((spiketrain >= t_start) & (spiketrain <= t_stop),
                      axis=axis) / (t_stop-t_start)
    else:
        # this is needed to handle broadcasting between spiketrain and t_stop
        t_stop_test = np.expand_dims(t_stop, axis)
        return np.sum((spiketrain >= t_start) & (spiketrain <= t_stop_test),
                      axis=axis) / (t_stop-t_start)


# we make `cv` an alias for scipy.stats.variation for the convenience
# of former NeuroTools users
cv = scipy.stats.variation


def fanofactor(spiketrains):
    """
    Evaluates the empirical Fano factor F of the spike counts of
    a list of `neo.core.SpikeTrain` objects.

    Given the vector v containing the observed spike counts (one per
    spike train) in the time window [t0, t1], F is defined as:

                        F := var(v)/mean(v).

    The Fano factor is typically computed for spike trains representing the
    activity of the same neuron over different trials. The higher F, the larger
    the cross-trial non-stationarity. In theory for a time-stationary Poisson
    process, F=1.

    Parameters
    ----------
    spiketrains : list of neo.SpikeTrain objects, quantity arrays, numpy arrays or lists
        Spike trains for which to compute the Fano factor of spike counts.

    Returns
    -------
    fano : float or nan
        The Fano factor of the spike counts of the input spike trains. If an
        empty list is specified, or if all spike trains are empty, F:=nan.
    """
    # Build array of spike counts (one per spike train)
    spike_counts = np.array([len(t) for t in spiketrains])

    # Compute FF
    if all([count == 0 for count in spike_counts]):
        fano = np.nan
    else:
        fano = spike_counts.var() / spike_counts.mean()
    return fano


def lv(v):
    """
    Calculate the measure of local variation LV for
    a sequence of time intervals between events.

    Given a vector v containing a sequence of intervals, the LV is
    defined as:

    .math $$ LV := \\frac{1}{N}\\sum_{i=1}^{N-1}

                   \\frac{3(isi_i-isi_{i+1})^2}
                          {(isi_i+isi_{i+1})^2} $$

    The LV is typically computed as a substitute for the classical
    coefficient of variation for sequences of events which include
    some (relatively slow) rate fluctuation.  As with the CV, LV=1 for
    a sequence of intervals generated by a Poisson process.

    Parameters
    ----------

    v : quantity array, numpy array or list
        Vector of consecutive time intervals

    Returns
    -------
    lvar : float
       The LV of the inter-spike interval of the input sequence.

    Raises
    ------
    AttributeError :
       If an empty list is specified, or if the sequence has less
       than two entries, an AttributeError will be raised.
    ValueError :
        Only vector inputs are supported.  If a matrix is passed to the
        function a ValueError will be raised.


    References
    ----------
    ..[1] Shinomoto, S., Shima, K., & Tanji, J. (2003). Differences in spiking
    patterns among cortical neurons. Neural Computation, 15, 2823–2842.


    """
    # convert to array, cast to float
    v = np.asarray(v)

    # ensure we have enough entries
    if v.size < 2:
        raise AttributeError("Input size is too small. Please provide "
                             "an input with more than 1 entry.")

    # calculate LV and return result
    # raise error if input is multi-dimensional
    return 3.*np.mean(np.power(np.diff(v)/(v[:-1] + v[1:]), 2))


#adaptation to output neo.AnalogSignal and wrapper make_kernel() in
#instantaneous_rate()
def make_kernel(form, sigma, sampling_period, direction=1):
    """
    Creates kernel functions for convolution.

    Constructs a numeric linear convolution kernel of basic shape to be used
    for data smoothing (linear low pass filtering) and firing rate estimation
    from single trial or trial-averaged spike trains.

    Exponential and alpha kernels may also be used to represent postynaptic
    currents / potentials in a linear (current-based) model.

    Parameters
    ----------
    form : {'BOX', 'TRI', 'GAU', 'EPA', 'EXP', 'ALP'}
        Kernel form. Currently implemented forms are BOX (boxcar),
        TRI (triangle), GAU (gaussian), EPA (epanechnikov), EXP (exponential),
        ALP (alpha function). EXP and ALP are asymmetric kernel forms and
        assume optional parameter `direction`.
    sigma : Quantity
        Standard deviation of the distribution associated with kernel shape.
        This parameter defines the time resolution of the kernel estimate
        and makes different kernels comparable (cf. [1] for symmetric kernels).
        This is used here as an alternative definition to the cut-off
        frequency of the associated linear filter.
    sampling_period : float
        Temporal resolution of input and output.
    direction : {-1, 1}
        Asymmetric kernels have two possible directions.
        The values are -1 or 1, default is 1. The
        definition here is that for direction = 1 the
        kernel represents the impulse response function
        of the linear filter. Default value is 1.

    Returns
    -------
    kernel : numpy.ndarray
        Array of kernel. The length of this array is always an odd
        number to represent symmetric kernels such that the center bin
        coincides with the median of the numeric array, i.e for a
        triangle, the maximum will be at the center bin with equal
        number of bins to the right and to the left.
    norm : float
        For rate estimates. The kernel vector is normalized such that
        the sum of all entries equals unity sum(kernel)=1. When
        estimating rate functions from discrete spike data (0/1) the
        additional parameter `norm` allows for the normalization to
        rate in spikes per second.

        For example:
        ``rate = norm * scipy.signal.lfilter(kernel, 1, spike_data)``
    m_idx : int
        Index of the numerically determined median (center of gravity)
        of the kernel function.

    Examples
    --------
    To obtain single trial rate function of trial one should use::

        r = norm * scipy.signal.fftconvolve(sua, kernel)

    To obtain trial-averaged spike train one should use::

        r_avg = norm * scipy.signal.fftconvolve(sua, np.mean(X,1))

    where `X` is an array of shape `(l,n)`, `n` is the number of trials and
    `l` is the length of each trial.

    See also
    --------
    elephant.statistics.instantaneous_rate

    References
    ----------

    .. [1] Meier R, Egert U, Aertsen A, Nawrot MP, "FIND - a unified framework
       for neural data analysis"; Neural Netw. 2008 Oct; 21(8):1085-93.

    .. [2] Nawrot M, Aertsen A, Rotter S, "Single-trial estimation of neuronal
       firing rates - from single neuron spike trains to population activity";
       J. Neurosci Meth 94: 81-92; 1999.

    """
    forms_abbreviated = np.array(['BOX', 'TRI', 'GAU', 'EPA', 'EXP', 'ALP'])
    forms_verbose = np.array(['boxcar', 'triangle', 'gaussian', 'epanechnikov',
                     'exponential', 'alpha'])
    if form in forms_verbose:
        form = forms_abbreviated[forms_verbose == form][0]

    assert form.upper() in ('BOX', 'TRI', 'GAU', 'EPA', 'EXP', 'ALP'), \
    "form must be one of either 'BOX','TRI','GAU','EPA','EXP' or 'ALP'!"

    assert direction in (1, -1), "direction must be either 1 or -1"

    # conversion to SI units (s)
    SI_sigma = sigma.rescale('s').magnitude
    SI_time_stamp_resolution = sampling_period.rescale('s').magnitude

    norm = 1./SI_time_stamp_resolution

    if form.upper() == 'BOX':
        w = 2.0 * SI_sigma * np.sqrt(3)
        # always odd number of bins
        width = 2 * np.floor(w / 2.0 / SI_time_stamp_resolution) + 1
        height = 1. / width
        kernel = np.ones((1, width)) * height  # area = 1

    elif form.upper() == 'TRI':
        w = 2 * SI_sigma * np.sqrt(6)
        halfwidth = np.floor(w / 2.0 / SI_time_stamp_resolution)
        trileft = np.arange(1, halfwidth + 2)
        triright = np.arange(halfwidth, 0, -1)  # odd number of bins
        triangle = np.append(trileft, triright)
        kernel = triangle / triangle.sum()  # area = 1

    elif form.upper() == 'EPA':
        w = 2.0 * SI_sigma * np.sqrt(5)
        halfwidth = np.floor(w / 2.0 / SI_time_stamp_resolution)
        base = np.arange(-halfwidth, halfwidth + 1)
        parabula = base**2
        epanech = parabula.max() - parabula  # inverse parabula
        kernel = epanech / epanech.sum()  # area = 1

    elif form.upper() == 'GAU':
        w = 2.0 * SI_sigma * 2.7  # > 99% of distribution weight
        halfwidth = np.floor(w / 2.0 / SI_time_stamp_resolution)  # always odd
        base = np.arange(-halfwidth, halfwidth + 1) * SI_time_stamp_resolution
        g = np.exp(
            -(base**2) / 2.0 / SI_sigma**2) / SI_sigma / np.sqrt(2.0 * np.pi)
        kernel = g / g.sum()

    elif form.upper() == 'ALP':
        w = 5.0 * SI_sigma
        alpha = np.arange(
            1, (
                2.0 * np.floor(w / SI_time_stamp_resolution / 2.0) + 1) +
            1) * SI_time_stamp_resolution
        alpha = (2.0 / SI_sigma**2) * alpha * np.exp(
            -alpha * np.sqrt(2) / SI_sigma)
        kernel = alpha / alpha.sum()  # normalization
        if direction == -1:
            kernel = np.flipud(kernel)

    elif form.upper() == 'EXP':
        w = 5.0 * SI_sigma
        expo = np.arange(
            1, (
                2.0 * np.floor(w / SI_time_stamp_resolution / 2.0) + 1) +
            1) * SI_time_stamp_resolution
        expo = np.exp(-expo / SI_sigma)
        kernel = expo / expo.sum()
        if direction == -1:
            kernel = np.flipud(kernel)

    kernel = kernel.ravel()
    m_idx = np.nonzero(kernel.cumsum() >= 0.5)[0].min()

    return kernel, norm, m_idx


def instantaneous_rate(spiketrain, sampling_period, form, sigma, m_idx=None,
                       t_start=None, t_stop=None, acausal=True, trim=False):

    """
    Estimate instantaneous firing rate by kernel convolution.

    Parameters
    -----------
    spiketrain: 'neo.SpikeTrain'
        Neo object that contains spike times, the unit of the time stamps
        and t_start and t_stop of the spike train.
    sampling_period : Quantity
        time stamp resolution of the spike times. the same resolution will
        be assumed for the kernel
    form : {'BOX', 'TRI', 'GAU', 'EPA', 'EXP', 'ALP'}
        Kernel form. Currently implemented forms are BOX (boxcar),
        TRI (triangle), GAU (gaussian), EPA (epanechnikov), EXP (exponential),
        ALP (alpha function). EXP and ALP are asymmetric kernel forms and
        assume optional parameter `direction`.
    sigma : Quantity
        Standard deviation of the distribution associated with kernel shape.
        This parameter defines the time resolution of the kernel estimate
        and makes different kernels comparable (cf. [1] for symmetric kernels).
        This is used here as an alternative definition to the cut-off
        frequency of the associated linear filter.
    t_start : Quantity (Optional)
        start time of the interval used to compute the firing rate, if None
        assumed equal to spiketrain.t_start
        Default:None
    t_stop : Qunatity
        End time of the interval used to compute the firing rate (included).
        If none assumed equal to spiketrain.t_stop
        Default:None
    acausal : bool
        if True, acausal filtering is used, i.e., the gravity center of the
        filter function is aligned with the spike to convolve
        Default:None
    m_idx : int
        index of the value in the kernel function vector that corresponds
        to its gravity center. this parameter is not mandatory for
        symmetrical kernels but it is required when asymmetrical kernels
        are to be aligned at their gravity center with the event times if None
        is assumed to be the median value of the kernel support
        Default : None
    trim : bool
        if True, only the 'valid' region of the convolved
        signal are returned, i.e., the points where there
        isn't complete overlap between kernel and spike train
        are discarded
        NOTE: if True and an asymmetrical kernel is provided
        the output will not be aligned with [t_start, t_stop]

    Returns
    -------
    rate : neo.AnalogSignalArray
        Contains the rate estimation in unit hertz (Hz).
        Has a property 'rate.times' which contains the time axis of the rate
        estimate. The unit of this property is the same as the resolution that
        is given as an argument to the function.

    See also
    --------

    elephant.statistics.make_kernel
    """
    kernel, norm, m_idx = make_kernel(form=form, sigma=sigma,
                                      sampling_period=sampling_period)
    units = pq.CompoundUnit("%s*s" % str(sampling_period.rescale('s').magnitude))
    spiketrain = spiketrain.rescale(units)
    if t_start is None:
        t_start = spiketrain.t_start
    else:
        t_start = t_start.rescale(spiketrain.units)

    if t_stop is None:
        t_stop = spiketrain.t_stop
    else:
        t_stop = t_stop.rescale(spiketrain.units)

    if m_idx is None:
        m_idx = kernel.size / 2

    time_vector = np.zeros(int((t_stop - t_start)) + 1)

    spikes_slice = spiketrain.time_slice(t_start, t_stop) \
        if len(spiketrain) else np.array([])

    for spike in spikes_slice:
        index = int((spike - t_start))
        time_vector[index] += 1

    r = norm * scipy.signal.fftconvolve(time_vector, kernel, 'full')
    if np.any(r < 0):
        warnings.warn('Instantaneous firing rate approximation contains '
                      'negative values, possibly caused due to machine '
                      'precision errors')

    if acausal:
        if not trim:
            r = r[m_idx:-(kernel.size - m_idx)]

        elif trim:
            r = r[2 * m_idx:-2*(kernel.size - m_idx)]
            t_start = t_start + m_idx * spiketrain.units
            t_stop = t_stop - ((kernel.size) - m_idx) * spiketrain.units

    else:
        if not trim:
            r = r[m_idx:-(kernel.size - m_idx)]

        elif trim:
            r = r[2 * m_idx:-2*(kernel.size - m_idx)]
            t_start = t_start + m_idx * spiketrain.units
            t_stop = t_stop - ((kernel.size) - m_idx) * spiketrain.units

    rate = neo.AnalogSignalArray(signal=r.reshape(r.size, 1),
                                 sampling_period=sampling_period,
                                 units=pq.Hz, t_start=t_start)

    return rate


def time_histogram(spiketrains, binsize, t_start=None, t_stop=None,
                   output='counts', binary=False):
    """
    Time Histogram of a list of :attr:`neo.SpikeTrain` objects.

    Parameters
    ----------
    spiketrains : List of neo.SpikeTrain objects
        Spiketrains with a common time axis (same `t_start` and `t_stop`)
    binsize : quantities.Quantity
        Width of the histogram's time bins.
    t_start, t_stop : Quantity (optional)
        Start and stop time of the histogram. Only events in the input
        `spiketrains` falling between `t_start` and `t_stop` (both included)
        are considered in the histogram. If `t_start` and/or `t_stop` are not
        specified, the maximum `t_start` of all :attr:spiketrains is used as
        `t_start`, and the minimum `t_stop` is used as `t_stop`.
        Default: t_start = t_stop = None
    output : str (optional)
        Normalization of the histogram. Can be one of:
        * `counts`'`: spike counts at each bin (as integer numbers)
        * `mean`: mean spike counts per spike train
        * `rate`: mean spike rate per spike train. Like 'mean', but the
          counts are additionally normalized by the bin width.
    binary : bool (optional)
        If **True**, indicates whether all spiketrain objects should first
        binned to a binary representation (using the `BinnedSpikeTrain` class
        in the `conversion` module) and the calculation of the histogram is
        based on this representation.
        Note that the output is not binary, but a histogram of the converted,
        binary representation.
        Default: False

    Returns
    -------
    time_hist : neo.AnalogSignalArray
        A neo.AnalogSignalArray object containing the histogram values.
        `AnalogSignal[j]` is the histogram computed between
        `t_start + j * binsize` and `t_start + (j + 1) * binsize`.

    See also
    --------
    elephant.conversion.BinnedSpikeTrain
    """
    min_tstop = 0
    if t_start is None:
        # Find the internal range for t_start, where all spike trains are
        # defined; cut all spike trains taking that time range only
        max_tstart, min_tstop = conv._get_start_stop_from_input(spiketrains)
        t_start = max_tstart
        if not all([max_tstart == t.t_start for t in spiketrains]):
            warnings.warn(
                "Spiketrains have different t_start values -- "
                "using maximum t_start as t_start.")

    if t_stop is None:
        # Find the internal range for t_stop
        if min_tstop:
            t_stop = min_tstop
            if not all([min_tstop == t.t_stop for t in spiketrains]):
                warnings.warn(
                    "Spiketrains have different t_stop values -- "
                    "using minimum t_stop as t_stop.")
        else:
            min_tstop = conv._get_start_stop_from_input(spiketrains)[1]
            t_stop = min_tstop
            if not all([min_tstop == t.t_stop for t in spiketrains]):
                warnings.warn(
                    "Spiketrains have different t_stop values -- "
                    "using minimum t_stop as t_stop.")

    sts_cut = [st.time_slice(t_start=t_start, t_stop=t_stop) for st in
               spiketrains]

    # Bin the spike trains and sum across columns
    bs = conv.BinnedSpikeTrain(sts_cut, t_start=t_start, t_stop=t_stop,
                               binsize=binsize)

    if binary:
        bin_hist = bs.to_sparse_bool_array().sum(axis=0)
    else:
        bin_hist = bs.to_sparse_array().sum(axis=0)
    # Flatten array
    bin_hist = np.ravel(bin_hist)
    # Renormalise the histogram
    if output == 'counts':
        # Raw
        bin_hist = bin_hist * pq.dimensionless
    elif output == 'mean':
        # Divide by number of input spike trains
        bin_hist = bin_hist * 1. / len(spiketrains) * pq.dimensionless
    elif output == 'rate':
        # Divide by number of input spike trains and bin width
        bin_hist = bin_hist * 1. / len(spiketrains) / binsize
    else:
        raise ValueError('Parameter output is not valid.')

    return neo.AnalogSignalArray(signal=bin_hist.reshape(bin_hist.size, 1),
                                 sampling_period=binsize, units=bin_hist.units,
                                 t_start=t_start)

