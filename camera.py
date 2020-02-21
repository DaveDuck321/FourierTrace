import pygame

class Shape():
    def draw(self, cam):
        raise Exception("NotImplementedException")

class Circle(Shape):
    def __init__(self, color, center, radius):
        self.color = color
        self.center = center
        self.radius = radius
    
    def draw(self, cam):
        c = cam.point_on_surface(cam.get_local_coords(self.center))
        r = int(self.radius/cam.radius * cam._RENDER_RADIUS)

        pygame.gfxdraw.aacircle(cam._surface, c[0], c[1], r, self.color)

class Line(Shape):
    def __init__(self, color, p1, p2):
        self.color = color
        self.p1 = p1
        self.p2 = p2

    def draw(self, cam):
        local1, local2 = cam.get_local_coords(self.p1), cam.get_local_coords(self.p2)
        p1, p2 = cam.point_on_surface(local1), cam.point_on_surface(local2)

        pygame.draw.aaline(cam._surface, self.color, p1, p2)

class Camera():
    def __init__(self, surface, render_radius, radius = 1):
        self._RENDER_RADIUS = render_radius
        self._surface = surface

        self.radius = radius
        self.center = 0

        self.draw_buffer = []

    def get_local_coords(self, point):
        return (point - self.center)/self.radius

    def point_on_surface(self, point):
        coord = ((point+1+1j) * self._RENDER_RADIUS)
        return int(coord.real), int(coord.imag)
    
    def add_shape(self, shape, zindex = 0):
        self.draw_buffer.append((zindex, shape))
    
    def flush(self):
        self.draw_buffer.sort(key = lambda i: i[0])
        while self.draw_buffer:
            self.draw_buffer.pop()[1].draw(self)

