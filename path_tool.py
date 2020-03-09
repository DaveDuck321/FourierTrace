"""
A tool for path generation.
Converts a series of argand vectors into their corresponding complex polar path
"""

import utils
import math

# Contant, experimentally determined
# Small values can produce more complex shapes but converge slowly
ANGLE_INC = 0.001


class PathCreate():
    def __init__(self):
        self.angle = 0
        self.path = []

    def revolutions(self):
        """Returns the number of revolutions required to produce the current path
        """
        return self.angle//(2*math.pi)

    def phase(self):
        """Returns the current phase of the cursor
        """
        return utils.phase(self.angle)

    def add_point(self, point):
        """Adds a complex vector to the path
        Returns the angle and complex value of new the path vector
        """
        point_angle = math.atan2(point.imag, point.real) % (math.pi*2)
        if utils.is_lagging(self.angle, point_angle):
            new_angle = point_angle + 2*math.pi * self.revolutions()

            if new_angle < self.angle:
                new_angle += 2*math.pi
            self.angle = new_angle
        else:
            self.angle += ANGLE_INC

        direction = utils.unit_direction(self.phase())
        selection = utils.convert_base(direction, point)

        self.path.append((self.angle, selection))
        return self.path[-1]
