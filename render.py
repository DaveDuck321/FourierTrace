"""
Renders a path to the screen using pygame
"""

from functools import partial
from itertools import islice

import pygame
import unwrap_path
from fourier import fourier_series, fourier_sum


import math

TEST_PATH = []
for n in range(-100, 100):
    TEST_PATH.append(1-n/100j)
for n in range(-100, 100):
    TEST_PATH.append(-n/100+1j)
for n in range(-100, 100):
    TEST_PATH.append(-1+n/100j)
for n in range(-100, 100):
    TEST_PATH.append(n/100-1j)

RENDER_RADIUS = 256
INTERNAL_RADIUS = 2

def stretch_to_screen(n):
    return int(n*RENDER_RADIUS/INTERNAL_RADIUS)

def center_on_screen(n):
    return int((n/INTERNAL_RADIUS)*RENDER_RADIUS + RENDER_RADIUS)

def complex_to_screen(t, z):
    return center_on_screen(z.real * math.cos(t)), center_on_screen(z.real * math.sin(t))

def plot_polar(screen, points):
    for point in points:
        coords = complex_to_screen(point[0], point[1])
        screen.set_at(coords, (0, 255, 255))
    for point in points:
        coords = (stretch_to_screen(point[0]), center_on_screen(point[1]))
        screen.set_at(coords, (0, 255, 0))

def cartesian_gen_plot(screen, period, gen):
    for n in range(1000):
        t = n/1000 * period
        mag = stretch_to_screen(sum(fourier_sum(gen, t)).real)
        screen.set_at((stretch_to_screen(t), mag), (0, 0, 255))

def path_plot(screen, period, path):
    for n in range(1000):
        t = n/1000 * period
        coords = stretch_to_screen(t), center_on_screen(path(t))
        screen.set_at(coords, (255, 0, 0))

def get_pixels(screen):
    POINTS = list(unwrap_path.points_to_polar(TEST_PATH))
    PERIOD = max(POINTS)[0]
    
    plot_polar(screen, POINTS)

    PATH = partial(unwrap_path.linear_extrapolate, POINTS)
    path_plot(screen, PERIOD, PATH)

    series = fourier_series(PATH, PERIOD)
    terminating = list(islice(series, 20))

    cartesian_gen_plot(screen, PERIOD, terminating)

    RESOLUTION = 1000
    return map(
        lambda t: complex_to_screen(t, sum(fourier_sum(terminating, t))),
        map (
            lambda n: PERIOD * n/RESOLUTION,
            range(RESOLUTION)
        )
    )

def main():
    # Init
    pygame.init()
    screen = pygame.display.set_mode((RENDER_RADIUS*2, RENDER_RADIUS*2))

    # Draw to screen
    for pixel in get_pixels(screen):
        screen.set_at(pixel, (255, 255, 255))

    # Gameloop
    running = True
    while running:
        pygame.display.flip()
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    print("Hello World")

if __name__ == "__main__":
    main()
