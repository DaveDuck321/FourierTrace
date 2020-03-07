"""
A tool for path generation.
Converts a series of argand vectors into their corresponding complex polar path
"""

import utils
import math

ANGLE_INC = 0.001


class PathCreate():
    def __init__(self):
        self.angle = 0
        self.path = []

    def add_point(self, point):
        """Adds a complex vector to the path
        Returns the angle and complex value of new the path vector
        """
        point_angle = math.atan2(point.imag, point.real) % (math.pi*2)
        if point_angle > self.angle:
            self.angle = point_angle
        else:
            self.angle += ANGLE_INC

        direction = utils.unit_direction(self.angle)
        selection = utils.convert_base(direction, point)

        self.path.append((self.angle, selection))
        return self.path[-1]
