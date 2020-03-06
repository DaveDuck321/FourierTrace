"""
Renders a path to the screen using pygame
"""

from functools import partial
from itertools import islice

import pygame
import sys, pickle, math

RENDER_RADIUS = 256
ANGLE_INC = 0.1

def screen_coord(z):
    coord = (z+1+1j)*RENDER_RADIUS
    return (
        int(coord.real),
        int(coord.imag)
    )

def dot(z1, z2):
    return z1.real*z2.real + z1.imag*z2.imag

def perp(z1):
    return complex(z1.imag, -z1.real)

def draw_image(screen, image, pos, scale = (RENDER_RADIUS*2, RENDER_RADIUS*2)):
    if image is not None:
        scaled = pygame.transform.scale(image, scale)
        screen.blit(scaled, pos)

def load_image(image_path):
    try:
        return pygame.image.load(image_path)
    except:
        print("Could not load image", file=sys.stderr)
        return None

def draw_line(screen, color, start, end):
    start = screen_coord(start)
    end = screen_coord(end)

    pygame.draw.aaline(screen, color, start, end)

def draw_guide_line(screen, angle, selected):
    direction = complex(math.cos(angle), math.sin(angle))
    draw_line(screen, (0, 180, 0), 0, direction*1000)

    start_guide = direction*selected.real
    end_guide = perp(direction) * selected.imag

    draw_line(screen, (255, 0, 0), start_guide, start_guide+end_guide)

def main(background_path, resolution):
    # Init
    pygame.init()
    background = load_image(background_path)
    screen = pygame.display.set_mode((RENDER_RADIUS*2, RENDER_RADIUS*2))

    angle, selection = 0, 0
    path = []

    # Gameloop
    display_background = True
    running = True
    while running:
        pygame.display.flip()

        # Draw to screen
        if display_background:
            draw_image(screen, background, (0, 0))
        draw_guide_line(screen, angle, selection)
        for angle, point in path:
            direction = complex(math.cos(angle), math.sin(angle))

            start_guide = direction*point.real
            end_guide = perp(direction) * point.imag
            screen.set_at(screen_coord(start_guide+end_guide), (255, 0, 0))
            #draw_line(screen, (255, 0, 0), start_guide, start_guide+end_guide)

        # Events
        for event in pygame.event.get():
            if (event.type == pygame.MOUSEMOTION and event.buttons[0] == 1) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                position = complex(
                    event.pos[0]/ RENDER_RADIUS - 1,
                    event.pos[1]/ RENDER_RADIUS - 1
                )
                cursor_angle = math.atan2(position.imag, position.real) % (math.pi*2)
                if cursor_angle > angle:
                    angle = cursor_angle
                else:
                    angle += resolution

                selection = complex(
                    math.cos(angle)*position.real + math.sin(angle)*position.imag,
                    math.sin(angle)*position.real - math.cos(angle)*position.imag
                )
                print(selection)

                path.append((angle, selection))
                #path.append(position)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    display_background = not display_background
                if event.key == pygame.K_RETURN:
                    with open("out.p", 'wb+') as out:
                        pickle.dump(path, out)

                    running = False

            if event.type == pygame.QUIT:
                running = False

    print("Finshed")

if __name__ == "__main__":
    main(sys.argv[2], float(sys.argv[1]))
