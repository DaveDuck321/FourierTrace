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
    terminating = list(islice(series, 10))

    RESOLUTION = 1000
    return map(
        lambda t: argand_to_screen(t, sum(fourier_sum(terminating, t))),
        map (
            lambda n: PERIOD * n/RESOLUTION,
            range(RESOLUTION)
        )
    )

def gen_draw_pendulum(lifetime=1):
    trail = []
    def draw_pendulum(camera, accumulation, focus):
        for p, c in zip(accumulation, accumulation[1:]):
            camera.add_shape( Line((255, 255, 255), p, c) )

            if p == accumulation[focus]:
                camera.add_shape( Circle((0, 255, 0), p, abs(p-c)) )
            else:
                camera.add_shape( Circle((0, 50, 255), p, abs(p-c)) )

        current_t = time.time()
        trail.append((current_t, accumulation[-1]))
        
        for i in range(len(trail))[::-1]:
            if current_t - trail[i][0] > lifetime:
                trail.pop(i)

        for (created, p1), (_, p2) in zip(trail, trail[1:]):
            intensity = 255 - int(255*(current_t-created)/ lifetime)
            camera.add_shape( Line((intensity, 0, 0), p1, p2), -created)

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

def get_focal_points(accumulation):
    local_radii = list(map(
        lambda p: abs(p[0]-p[1]),
        zip(accumulation, accumulation[1:])
    ))
    global_radii = [0]+list(accumulate(local_radii))

    return list(map(
        lambda node: ( node[0], global_radii[-1]-global_radii[node[0]] ),
        filter(
            lambda node: node[1] > 0.01,
            enumerate(local_radii)
        )
    ))

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

    draw_pendulum = gen_draw_pendulum(6)
    radial_accumulation = gen_radial_accumulation(TEST_PATH)

    # Gameloop
    d_time = 1/60
    running = True

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

        camera.flush()
        pygame.display.flip()

        # Timing
        d_time = t()
        # Events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    focus = min(focus+1, len(focal_points)-1)
                    camera.radius = focal_points[focus][1]
                if event.key == pygame.K_LEFT:
                    focus = max(0, focus-1)
                    camera.radius = focal_points[focus][1]
            if event.type == pygame.QUIT:
                running = False

    print("Hello World")

if __name__ == "__main__":
    main()
