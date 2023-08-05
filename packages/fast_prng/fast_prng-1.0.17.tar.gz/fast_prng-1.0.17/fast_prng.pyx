#cython: cdivision=True
#cython: overflowcheck=False

from numpy cimport ndarray
import numpy as np

cdef extern from "fast_prng/exponential.h":
    double c_exponential "exponential"()

cdef extern from "fast_prng/normal.h":
    double c_normal "normal"()

cdef extern from "fast_prng/MT19937.h":
    void mt_init()
    double c_uniform "uniform_double_PRN"()

mt_init()       #Initializes all PRNGs

def exponential(double scale=1.0, size=1):
    """exponential(scale=1.0, size=1)

Exponential distribution.

Its probability density function is

.. math:: f(x; \frac{1}{\beta}) = \frac{1}{\beta} \exp(-\frac{x}{\beta}),

for ``x > 0`` and 0 elsewhere. :math:`\beta` is the scale parameter,
which is the inverse of the rate parameter :math:`\lambda = 1/\beta`.
The rate parameter is an alternative, widely used parameterization
of the exponential distribution.

Parameters
----------
scale : float
    The scale parameter, :math:`\beta = 1/\lambda`.
size : tuple of ints
    Number of samples to draw.  The output is shaped
    according to `size`.

See https://bitbucket.org/cdmcfarland/fast_prns for further details.
"""
    if size == 1:
        return scale*c_exponential()

    cdef long total_size = np.multiply.reduce(size)
    cdef double *element
    cdef double *end    
    cdef ndarray[dtype=double, ndim=1] output = np.empty(total_size, order='C')
    
    element = &(output[0]) 
    end = element + total_size
        
    if scale != 1.0:
        while element < end:
            element[0] = scale*c_exponential()
            element += 1
    else:
        while element < end:
            element[0] = c_exponential()
            element += 1
    return output.reshape(size)

def normal(double loc=0.0, double scale=1.0, size=1):
    """normal(loc=0.0, scale=1.0, size=1)

Draw random samples from a normal (Gaussian) distribution.

The probability density function:

        p(x) = 1/sqrt(2*pi*sigma**2)*exp( -(x - loc)**2/(2*sigma^2) ),

    where mu = loc, scale = sigma, and sqrt/pi/exp are defined in numpy. 

Parameters
----------
loc : float
    Mean ("centre") of the distribution.
scale : float
    Standard deviation (spread or "width") of the distribution.
size : tuple of ints
    Output shape.  If the given shape is, e.g., ``(m, n, k)``, then
    ``m * n * k`` samples are drawn.

See https://bitbucket.org/cdmcfarland/fast_prns for further details. 
"""
    if size == 1:
        return scale*c_normal() + loc

    cdef long total_size = np.multiply.reduce(size) 
    cdef double *element
    cdef double *end
    cdef ndarray[dtype=double, ndim=1] output = np.empty(total_size, order='C')

    element = &(output[0])
    end = element + total_size
    if scale != 1.0:
        if loc != 0:
            while element < end:
                element[0] = scale*c_normal() + loc
                element += 1
        else:
            while element < end:
                element[0] = scale*c_normal()
                element += 1
    else:
        if loc != 0:
            while element < end:
                element[0] = c_normal() + loc
                element += 1
        else:
            while element < end:
                element[0] = c_normal()
                element += 1
    return output.reshape(size)

def uniform(double low=0, double high=1, size=1):
    """uniform(low=0.0, high=1.0, size=None)

Draw samples from a uniform distribution.

Samples are uniformly distributed over the half-open interval
``[low, high)`` (includes low, but excludes high).  In other words,
any value within the given interval is equally likely to be drawn
by `uniform`.

Parameters
----------
low : float, optional
    Lower boundary of the output interval.  All values generated will be
    greater than or equal to low.  The default value is 0.
high : float
    Upper boundary of the output interval.  All values generated will be
    less than high.  The default value is 1.0.
size : int or tuple of ints, optional
    Output shape.  If the given shape is, e.g., ``(m, n, k)``, then
    ``m * n * k`` samples are drawn.  Default is None, in which case a
    single value is returned.

Returns
-------
out : ndarray
    Drawn samples, with shape `size`.
See https://bitbucket.org/cdmcfarland/fast_prns for further details. 
"""
    cdef double scale = high - low
    if size == 1:
        return scale*c_uniform() + low

    cdef long total_size = np.multiply.reduce(size) 
    cdef double *element
    cdef double *end
    cdef ndarray[dtype=double, ndim=1] output = np.empty(total_size, order='C')

    element = &(output[0])
    end = element + total_size
    if scale != 1.0:
        if low != 0:
            while element < end:
                element[0] = scale*c_uniform() + low
                element += 1
        else:
            while element < end:
                element[0] = scale*c_uniform()
                element += 1
    else:
        if low != 0:
            while element < end:
                element[0] = c_uniform() + low
                element += 1
        else:
            while element < end:
                element[0] = c_uniform()
                element += 1
    return output.reshape(size)

