"""
Tools to convert cartesian coordinates to a polar path
"""

from bisect import bisect_right


def linear_extrapolater(points):
    """Returns a function with argument 'phase'.
    This linearly extrapolates between the phase-value pairs in 'points'
    in order to calculate the complex value at a given phase
    """
    points = sorted(points)

    def extrapolate(phase):
        index = bisect_right(points, (phase,))

        angle1, z1 = points[index - 1]
        angle2, z2 = points[index]

        gradient = (z1-z2) / (angle1-angle2)
        return z1 + gradient * (phase - angle1)

    return extrapolate
