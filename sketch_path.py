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

    start_guide = direction*(direction.real*selected.real + direction.imag*selected.imag)
    draw_line(screen, (255, 0, 0), start_guide, selected)

def main(background_path):
    # Init
    pygame.init()
    background = load_image(background_path)
    screen = pygame.display.set_mode((RENDER_RADIUS*2, RENDER_RADIUS*2))

    angle_index, selection = 0, 0
    path = []
    # Gameloop
    running = True
    while running:
        pygame.display.flip()

        # Draw to screen
        draw_image(screen, background, (0, 0))
        draw_guide_line(screen, ANGLE_INC*angle_index, selection)
        for angle, p in path:
            screen.set_at(screen_coord(p), (0, 0, 255))

        # Events
        for event in pygame.event.get():
            if (event.type == pygame.MOUSEMOTION and event.buttons[0] == 1) or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                position = complex(
                    event.pos[0]/ RENDER_RADIUS - 1,
                    event.pos[1]/ RENDER_RADIUS - 1
                )
                selection = position
                #path.append(position)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if len(path) <= angle_index:
                        path.append((angle_index*ANGLE_INC, selection))
                    else:
                        path[angle_index] = (angle_index*ANGLE_INC, selection)
                        selection = path[angle_index+1][1]
                    angle_index += 1
                if event.key == pygame.K_LEFT:
                    angle_index -= 1
                    selection = path[angle_index][1]
                if event.key == pygame.K_RETURN:
                    with open("out.p", 'wb+') as out:
                        pickle.dump(path, out)

                    running = False

            if event.type == pygame.QUIT:
                running = False

    print("Finshed")

if __name__ == "__main__":
    main(sys.argv[1])
