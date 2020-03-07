"""
Some complex vector math utils
"""

import math


def unit_direction(angle):
    """Returns a complex unit vector with direction specified by 'angle'
    """
    return complex(math.cos(angle), math.sin(angle))


def dot(z1, z2):
    """Returns the dot product of two complex position vecotrs
    """
    return z1.real*z2.real + z1.imag*z2.imag


def perpendicular(z):
    """Returns a complex vector perpendicular to z
    """
    return complex(z.imag, -z.real)


def convert_base(base, z):
    """Converts a complex vector into base 'base'.
    'base' is a unit direction representing the new base
    """
    return complex(
        dot(base, z),
        dot(perpendicular(base), z)
    )
