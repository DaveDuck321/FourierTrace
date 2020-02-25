"""
Tools to convert cartesian coordinates to a polar path
"""

from functools import partial
from bisect import bisect_right

import math
import fourier

def complex_to_polar(z):
    
    result = math.atan2(z.imag, z.real)
    if result < 0:
        return (2*math.pi + result, abs(z))
        
    return (result, abs(z))

def points_to_polar(points):
    return map(
        complex_to_polar,
        points
    )

def limit_positive_angle(angle):
    if angle < 0:
        return 2*math.pi + angle
    return angle

def unwrap_to_polar(cartesian):
    points = points_to_polar(cartesian)
    first = next(points)

    unwrapped = [(0, first[1])]
    offset = first[0]
    previous_phase, revolutions = 0, 0

    for (phase, mag) in points:
        phase = limit_positive_angle(phase-offset)
        if phase < previous_phase:
            revolutions += 1

        previous_phase = phase
        unwrapped.append((phase + 2*math.pi*revolutions, mag))

    return (offset, unwrapped)


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