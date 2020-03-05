"""
Renders a path to the screen using pygame
"""

from functools import partial
from itertools import islice

RENDER_RADIUS = 256

import pygame
import pickle

def main():
    # Init
    pygame.init()
    screen = pygame.display.set_mode((RENDER_RADIUS*2, RENDER_RADIUS*2))

    path = [0]
    # Gameloop
    running = True
    while running:
        pygame.display.flip()

        # Draw to screen
        for coord in path:
            pixel = (
                int((coord.real + 1) * RENDER_RADIUS),
                int((coord.imag + 1) * RENDER_RADIUS)
            )
            screen.set_at(pixel, (255, 255, 255))

        # Events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
                position = complex(
                    event.pos[0]/ RENDER_RADIUS - 1,
                    event.pos[1]/ RENDER_RADIUS - 1
                )
                path.append(position)
                print(position)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                with open("out.p", 'wb+') as out:
                    pickle.dump(path[1:], out)

                running = False

            if event.type == pygame.QUIT:
                running = False

    print("Finshed")

if __name__ == "__main__":
    main()
