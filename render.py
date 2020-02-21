"""
Renders a path to the screen using pygame
"""

from fourier import fourier_series, fourier_sum
from camera import Camera, Circle, Line
import unwrap_path

from functools import partial
from itertools import islice, accumulate, tee, chain
import math, time


import pygame
from pygame import gfxdraw

RENDER_RADIUS = 256

def timer():
    start = time.time()
    return lambda: time.time()-start

def argand_transform(t, z):
    return (
        complex(
            z.real * math.cos(t) + z.imag * math.sin(t),
            z.real * math.sin(t) - z.imag * math.cos(t),
        )
    )

def get_pixels(POINTS):
    POINTS = list(unwrap_path.points_to_polar(POINTS))
    PERIOD = max(POINTS)[0]

    PATH = unwrap_path.linear_extrapolater(POINTS)

    series = fourier_series(PATH, PERIOD)
    terminating = list(islice(series, 20))

    RESOLUTION = 1000
    return map(
        lambda t: argand_to_screen(t, sum(fourier_sum(terminating, t))),
        map (
            lambda n: PERIOD * n/RESOLUTION,
            range(RESOLUTION)
        )
    )

def gen_draw_pendulum():
    trail = []
    def draw_pendulum(camera, accumulation):
        for p, c in zip(accumulation, accumulation[1:]):
            camera.add_shape( Line((255, 255, 255), p, c) )
            camera.add_shape( Circle((0, 255, 0), p, abs(p-c) ) )

        trail.append(accumulation[-1])
        for p1, p2 in zip(trail, trail[1:]):
            camera.add_shape( Line((0, 0, 255), p1, p2) )

    return draw_pendulum

def gen_radial_accumulation(POINTS):
    POINTS = list(unwrap_path.points_to_polar(POINTS))
    PERIOD = max(POINTS)[0]

    PATH = unwrap_path.linear_extrapolater(POINTS)

    series = fourier_series(PATH, PERIOD)
    terminating = list(islice(series, 100))

    def radial_accumulation(t):
        return [0]+list(map(
            partial(argand_transform, t),
            accumulate(fourier_sum(terminating, t))
        ))

    return radial_accumulation

def main():
    TEST_PATH = []
    for n in range(-100, 100):
        TEST_PATH.append(1-n/100j)
    for n in range(-100, 100):
        TEST_PATH.append(-n/100+1j)
    for n in range(-100, 100):
        TEST_PATH.append(-1+n/100j)
    for n in range(-100, 100):
        TEST_PATH.append(n/100-1j)

    # Init
    pygame.init()
    screen = pygame.display.set_mode((RENDER_RADIUS*2, RENDER_RADIUS*2))
    camera = Camera(screen, RENDER_RADIUS, 2)

    draw_pendulum = gen_draw_pendulum()
    radial_accumulation = gen_radial_accumulation(TEST_PATH)

    # Gameloop
    d_time = 1/60
    running = True

    rotation = 0
    while running:
        # Frame logic
        t = timer()
        rotation += d_time
        accumulation = radial_accumulation(rotation)

        # Drawing
        screen.fill((0, 0, 0))
        draw_pendulum(camera, accumulation)

        camera.center = accumulation[1]
        camera.radius = 0.5

        camera.flush()
        pygame.display.flip()


        # Timing
        d_time = t()
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    print("Hello World")

if __name__ == "__main__":
    main()
