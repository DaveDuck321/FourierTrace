"""
Tools to convert cartesian coordinates to a polar path
"""

from functools import partial
from bisect import bisect_right

import math
import fourier

def atan3(y, x):
    result = math.atan2(y, x)
    if result < 0:
        return 2*math.pi + result
    return result

def points_to_polar(points):
    previousPhase, phaseOffset = 0, 0

    for point in points:
        phase = atan3(point.imag, point.real)
        if phase < previousPhase:
            #phaseOffset += 2*math.pi
            pass

        previousPhase = phase
        yield phase + phaseOffset, abs(point)


def linear_extrapolater(points):
    points = sorted(points)
    
    def extrapolate(point):
        index = bisect_right(points, (point,))
        previous, current = points[index - 1], points[index]

        gradient = (previous[1]-current[1]) / (previous[0]-current[0])
        return previous[1] + gradient*(point-previous[0])

    return extrapolate


if __name__ == "__main__":
    TEST_PATH = [-1-1j, -1+1j, 1+1j, 1-1j]

    POINTS = points_to_polar(TEST_PATH)
    PATH = partial(linear_extrapolate, POINTS)

    coefficients = fourier.fourier_coefficients(PATH, 2*math.pi)

    for i in range(5):
        print(next(coefficients))