"""
Renders a path to the screen using pygame
"""

from fourier import fourier_series, fourier_sum
import unwrap_path

from functools import partial
from itertools import islice, accumulate, tee, chain
import math, time


import pygame
from pygame import gfxdraw

RENDER_RADIUS = 256
INTERNAL_RADIUS = 2

def timer():
    start = time.time()
    return lambda: time.time()-start

def stretch_to_screen(n):
    return int(n*RENDER_RADIUS/INTERNAL_RADIUS)

def center_on_screen(n):
    return int((n/INTERNAL_RADIUS)*RENDER_RADIUS + RENDER_RADIUS)

def argand_to_screen(t, z):
    return (
        center_on_screen( z.real * math.cos(t) + z.imag * math.sin(t) ),
        center_on_screen( z.real * math.sin(t) - z.imag * math.cos(t))
    )

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

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

def gen_draw_pendulum(POINTS):
    POINTS = list(unwrap_path.points_to_polar(POINTS))
    PERIOD = max(POINTS)[0]

    PATH = unwrap_path.linear_extrapolater(POINTS)

    series = fourier_series(PATH, PERIOD)
    terminating = list(islice(series, 100))

    trail = []
    def draw_pendulum(screen, t):
        accumulation = [0]+list(accumulate(fourier_sum(terminating, t)))

        for p, c in zip(accumulation, accumulation[1:]):
            screen_p = argand_to_screen(t, p)
            screen_c = argand_to_screen(t, c)

            dist = stretch_to_screen(abs(c-p))
            if dist < 1:
                continue

            pygame.gfxdraw.aacircle(screen, screen_p[0], screen_p[1], dist, (0, 255, 0))
            pygame.draw.aaline(screen, (255, 255, 255), screen_p, screen_c)

        trail.append(argand_to_screen(t, accumulation[-1]))
        for p1, p2 in zip(trail, trail[1:]):
            pygame.draw.aaline(screen, (0, 0, 255), p1, p2)
        
    return draw_pendulum

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

    # Draw to screen
    #for pixel in get_pixels(TEST_PATH):
    #    screen.set_at(pixel, (255, 255, 255))

    draw_pendulum = gen_draw_pendulum(TEST_PATH)

    # Gameloop
    d_time = 1/60
    running = True

    rotation = 0
    while running:
        # Frame logic
        t = timer()
        rotation += d_time

        # Drawing
        screen.fill((0, 0, 0))
        draw_pendulum(screen, rotation)
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
