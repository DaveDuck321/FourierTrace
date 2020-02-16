"""
Tools to create fourier series
"""

import math
from functools import partial
from itertools import count

def product_integral(f1, f2, lower, upper, steps=1000):
    """Performs a numerical integration of the product f1(t)*f2(t)
    The integral is taken between the points 'lower' and 'upper'
    Steps defines the precision of the calculation
    """
    resolution = (upper-lower)/steps
    return sum(
        map(
            lambda point: f1(point) * f2(point),
            map(
                lambda n: n*resolution+lower,
                range(steps)
            )
        )
    ) * resolution

def cycle_coefficients():
    """Returns an iterator in the range -inf -- +inf
    Lower frequency results are output first

    0, 1, -1, 2, -2, ...
    """
    yield 0
    for n in count(1):
        yield n
        yield -n

def complex_harmonic(period, sign, n, t):
    """Returns the complex exponent of the input sinusoid
    """
    return math.e ** ((2j*math.pi*sign*n*t)/period)

def fourier_sum(series, t):
    """Returns an iterator of values representing each successive term in the fourier series
    CONSUMES the series iterator
    """
    return map(
        lambda term: term(t),
        series
    )

def fourier_series(f, period):
    """Returns an iterator of functions representing the terms in the fourier series
    """
    harmonic = partial(complex_harmonic, period, 1)
    return map(
        lambda val: ( lambda t: val[1] * harmonic(val[0], t) ),
        fourier_coefficients(f, period)
    )

def fourier_coefficients(f, period):
    """Returns an iterator of tuples (int, complex)
    Index 0 represents the index of this term in the Fourier series (0 is the constant term)
    Index 1 represents the complex coefficient
    """
    for n in cycle_coefficients():
        dot = partial(complex_harmonic, period, -1, n)
        yield (n, 1/period * product_integral(
            f, dot, 0, period
        ))