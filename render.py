"""
Renders a path to the screen using pygame
"""

from fourier import fourier_series, fourier_sum
from camera import Camera, Circle, Line
import extrapolate

from functools import partial
from itertools import islice, accumulate

import math
import time
import sys
import pickle

import pyglet
from pyglet import window
from pyglet.window import key

RENDER_RADIUS = 512


def argand_transform(t, z):
    return (
        complex(
            z.real * math.cos(t) + z.imag * math.sin(t),
            z.real * math.sin(t) - z.imag * math.cos(t),
        )
    )


def gen_radial_accumulation(POINTS):
    PERIOD = 2*math.pi * (max(POINTS)[0]//(2*math.pi) + 1)

    PATH = extrapolate.linear_extrapolater(POINTS)

    series = fourier_series(PATH, PERIOD)
    terminating = list(islice(series, 1000))

    def radial_accumulation(t):
        return [0]+list(map(
            partial(argand_transform, t),
            accumulate(fourier_sum(terminating, t))
        ))

    return radial_accumulation


def get_focal_points(accumulation):
    local_radii = list(map(
        lambda p: abs(p[0]-p[1]),
        zip(accumulation, accumulation[1:])
    ))
    global_radii = [0]+list(accumulate(local_radii))

    return list(map(
        lambda node: (node[0], global_radii[-1]-global_radii[node[0]]),
        filter(
            lambda node: node[1] > 0.01,
            enumerate(local_radii)
        )
    ))


class Controller(pyglet.window.Window):
    def __init__(self, path, **argv):
        super(Controller, self).__init__(
            RENDER_RADIUS*2,
            RENDER_RADIUS*2,
            **argv
        )

        self.trail = []

        self.rotation = 0
        self.focus = 0

        self.camera = Camera(RENDER_RADIUS, 2)

        self.radial_accumulation = gen_radial_accumulation(path)
        self.focal_points = get_focal_points(self.radial_accumulation(0))

        pyglet.clock.schedule_interval(self.on_update, 1/60)

    def on_update(self, dt):
        self.rotation += dt / ((self.focus+3)//2)
        self.camera.tick(dt)

    def on_draw(self):
        self.clear()

        accumulation = self.radial_accumulation(self.rotation)
        self.draw_pendulum(accumulation)

        self.camera.center = accumulation[self.focal_points[self.focus][0]]

        self.camera.flush()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.RIGHT:
            self.move_focus(1)
        if symbol == key.LEFT:
            self.move_focus(-1)

    def move_focus(self, direction):
        self.focus = max(0, min(self.focus+direction, len(self.focal_points)-1))
        self.camera.animate_radius(self.focal_points[self.focus][1])

    def draw_pendulum(self, accumulation):
        for p, c in zip(accumulation, accumulation[1:]):
            self.camera.add_shape(Line((255, 255, 255), p, c))

            if p == accumulation[self.focal_points[self.focus][0]]:
                self.camera.add_shape(Circle((0, 255, 0), p, abs(p-c)))
            else:
                self.camera.add_shape(Circle((0, 50, 255), p, abs(p-c)))

        current_t = time.time()
        self.trail.append((current_t, accumulation[-1]))

        for i in range(len(self.trail))[::-1]:
            if current_t - self.trail[i][0] > 1000:
                self.trail.pop(i)

        for (created, p1), (_, p2) in zip(self.trail, self.trail[1:]):
            intensity = 255 - int(255*(current_t-created) / 1000)
            self.camera.add_shape(Line((intensity, 0, 0), p1, p2))


if __name__ == "__main__":
    config = pyglet.gl.Config(sample_buffers=1, samples=4)
    with open(sys.argv[1], 'rb') as file:
        window = Controller(pickle.load(file), config=config)
    pyglet.app.run()
