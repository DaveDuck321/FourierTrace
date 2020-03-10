"""
Renders a path to the screen using pygame
"""

from fourier import fourier_series, fourier_sum
from camera import Camera, Circle, Line
import extrapolate

from functools import partial
from itertools import islice, accumulate, count, tee

import math
import time
import sys
import pickle

import pygame

RENDER_RADIUS = 512


def timer():
    start = time.time()
    return lambda: time.time()-start


def argand_transform(t, z):
    """Returns an argand point representing a complex polar coordinate at angle t
    """
    return (
        complex(
            z.real * math.cos(t) + z.imag * math.sin(t),
            z.real * math.sin(t) - z.imag * math.cos(t),
        )
    )


def gen_draw_pendulum(lifetime=1):
    """Returns a function that plots the array of pendulums and a point trail
    """
    trail = []

    def draw_pendulum(camera, accumulation, focus):
        """Plots the pendulums representing the current fourier accumulation
        """
        for index, (p, c) in enumerate(zip(accumulation, accumulation[1:])):
            circle_color = (0, 50, 255, max(255-abs(index-focus)**2, 30))
            line_color = (255, 255, 255, 50)

            if index == focus:
                circle_color = (0, 255, 0)
                line_color = (255, 255, 255)

            if index != 0:
                camera.add_shape(Circle(circle_color, p, abs(p-c)))
            camera.add_shape(Line(line_color, p, c))

        current_t = time.time()
        trail.append((current_t, accumulation[-1]))

        for i in range(len(trail))[::-1]:
            if current_t - trail[i][0] > lifetime:
                trail.pop(i)

        for (created, p1), (_, p2) in zip(trail, trail[1:]):
            intensity = 255 - int(255*(current_t-created) / lifetime)
            camera.add_shape(Line((intensity, 0, 0), p1, p2), -created)

    return draw_pendulum


def gen_radial_accumulation(POINTS, n=1000):
    """Calculates fourier coefficients and returns an expansion function
    This generate a fourier accumulation at a given angle with 'n' terms
    """
    PERIOD = 2*math.pi * (max(POINTS)[0]//(2*math.pi) + 1)

    PATH = extrapolate.linear_extrapolater(POINTS)

    series = fourier_series(PATH, PERIOD)
    terminating = list(islice(series, n))

    def radial_accumulation(t):
        return [0]+list(map(
            partial(argand_transform, t),
            accumulate(fourier_sum(terminating, t))
        ))

    return radial_accumulation


def get_focal_points(accumulation):
    """Returns a list of coefficient indexes and their outer_radius.
    These significantly contribute to the overall shape.
    """
    global_radii = [0]+list(accumulate(
        map(
            lambda p: abs(p[0]-p[1]),
            zip(accumulation, accumulation[1:])
        )
    ))

    # A pair of iterators representing the radius of the expansion at each term
    outer_radii = tee(map(
        lambda radii: (global_radii[-1] - radii)/2,
        global_radii
    ))
    # Skip the first term, so zip() can alternate values
    next(outer_radii[1])

    # Returns a list of the index and outer radius of each term
    # Filter removes terms that dont make a significant contribution to radius
    return list(
        filter(
            lambda val: val[1]*0.99 > val[2],
            zip(count(), *outer_radii)
        )
    )


def is_key_held(keys_down, key, hold_delay=0.2):
    """Return True if 'key' is currently held down.
    There is a delay of 'hold_delay' seconds after a key is initially pressed
    """
    return key in keys_down and time.time() - keys_down[key] > hold_delay


def update_focus(camera, focal_points, focus, direction):
    """Returns the new focus index and updates the camera's focus.
    Diection is a signed integer representing the sign of this change
    """
    focus = max(0, min(focus+direction, len(focal_points)-1))
    camera.animate_radius(focal_points[focus][1])
    return focus


def main(path):
    # Init
    pygame.init()
    screen = pygame.display.set_mode((RENDER_RADIUS*2, RENDER_RADIUS*2))
    camera = Camera(screen, RENDER_RADIUS, 2)

    draw_pendulum = gen_draw_pendulum(60)
    radial_accumulation = gen_radial_accumulation(path)

    # Gameloop
    d_time = 1/60
    running = True
    keys_down = {}

    focus = 0
    focal_points = get_focal_points(radial_accumulation(0))

    rotation = 0
    while running:
        # Frame logic
        t = timer()
        # Dilate time while zoomed in -- match rotation speed
        rotation += d_time / ((focus+3)//2)
        accumulation = radial_accumulation(rotation)

        # Drawing
        screen.fill((0, 0, 0))
        draw_pendulum(camera, accumulation, focal_points[focus][0])

        camera.center = accumulation[focal_points[focus][0]]

        camera.tick(d_time)
        camera.flush()
        pygame.display.flip()

        # Timing
        d_time = t()

        if is_key_held(keys_down, pygame.K_RIGHT, 0.2):
            keys_down[pygame.K_RIGHT] = time.time()-0.15
            focus = update_focus(camera, focal_points, focus, 1)
        if is_key_held(keys_down, pygame.K_LEFT, 0.2):
            keys_down[pygame.K_LEFT] = time.time()-0.15
            focus = update_focus(camera, focal_points, focus, -1)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key in keys_down:
                    del keys_down[event.key]
            if event.type == pygame.KEYDOWN:
                # Log keypress times
                keys_down[event.key] = time.time()

                if event.key == pygame.K_RIGHT:
                    focus = update_focus(camera, focal_points, focus, 1)
                if event.key == pygame.K_LEFT:
                    focus = update_focus(camera, focal_points, focus, -1)
            if event.type == pygame.QUIT:
                running = False


if __name__ == "__main__":
    with open(sys.argv[1], 'rb') as file:
        path = pickle.load(file)
    main(path)
