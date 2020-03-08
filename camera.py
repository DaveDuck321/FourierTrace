import pyglet
from collections import defaultdict

class Shape():
    def draw(self, batch):
        raise Exception("NotImplementedException")


class Circle(Shape):
    def __init__(self, color, center, radius):
        self.color = color
        self.center = center
        self.radius = radius

    def draw(self, cam, batch):
        c = cam.point_on_surface(cam.get_local(self.center))
        r = int(self.radius/cam.radius * cam._RENDER_RADIUS)

        # TODO: Circle render
        """
        batch.add(
            4,
            pyglet.gl.GL_LINES,
            None,
            ('v2i', (c[0]-r, c[1]-r, c[0]-r, c[1]+r, c[0]+r, c[1]+r, c[0]+r, c[1]-r)),
            ('c3B', (*self.color, *self.color, *self.color, *self.color))
        )"""


class Line(Shape):
    def __init__(self, color, p1, p2):
        self.color = color
        self.p1 = p1
        self.p2 = p2

    def draw(self, cam, batch):
        local1, local2 = cam.get_local(self.p1), cam.get_local(self.p2)
        p1, p2 = cam.point_on_surface(local1), cam.point_on_surface(local2)

        batch.add(
            2,
            pyglet.gl.GL_LINES,
            None,
            ('v2i', (p1[0], p1[1], p2[0], p2[1])),
            ('c3B', (*self.color, *self.color))
        )


class Camera():
    def __init__(self, render_radius, radius=1):
        self._RENDER_RADIUS = render_radius

        self.center = 0
        self.radius = radius

        self._target_radius = radius
        self._animate_speed = 10

        self.draw_buffer = []

    def get_local(self, point):
        return (point - self.center)/self.radius

    def point_on_surface(self, point):
        coord = ((point+1+1j) * self._RENDER_RADIUS)
        return int(coord.real), int(coord.imag)

    def animate_radius(self, target):
        self._target_radius = target

    def add_shape(self, shape):
        self.draw_buffer.append(shape)

    def tick(self, dt):
        self.radius += (self._target_radius-self.radius)*dt*self._animate_speed

    def flush(self):
        batch = pyglet.graphics.Batch()
        while self.draw_buffer:
            self.draw_buffer.pop().draw(self, batch)
        batch.draw()
