"""
Tool for constructing a path for rendering
"""

import math
import pickle
import sys

import pygame

RENDER_RADIUS = 256
ANGLE_INC = 0.001


def to_screen_coord(z):
    """Converts a complex position vector to an pixel screen coordinate
    """
    coord = (z+1+1j)*RENDER_RADIUS
    return (
        int(coord.real),
        int(coord.imag)
    )


def from_screen_coord(point):
    """Converts a pixel screen coordinate to a complex position vector
    """
    return complex(
        point[0]/RENDER_RADIUS - 1,
        point[1]/RENDER_RADIUS - 1
    )


def unit_direction(angle):
    """Returns a complex unit vector with direction specified by 'angle'
    """
    return complex(math.cos(angle), math.sin(angle))


def dot(z1, z2):
    """Returns the dot product of two complex position vecotrs
    """
    return z1.real*z2.real + z1.imag*z2.imag


def perpendicular(z):
    """Returns a complex vector perpendicular to z
    """
    return complex(z.imag, -z.real)


def convert_base(base, z):
    """Converts a complex vector into base 'base'.
    'base' is a unit direction representing the new base
    """
    return complex(
        dot(base, z),
        dot(perpendicular(base), z)
    )


def mouse_down_event(event, btn):
    """Returns a boolean.
    True <= The event implies btn is pressed down
    False <= The event is inconclusive
    """
    return (
        event.type == pygame.MOUSEMOTION and event.buttons[0] == 1
    ) or (
        event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
    )


def draw_image(screen, image, pos, size=(RENDER_RADIUS*2, RENDER_RADIUS*2)):
    """Draws an pygame image to the screen with position 'pos' and size 'size'
    """
    if image is not None:
        scaled = pygame.transform.scale(image, size)
        screen.blit(scaled, pos)


def load_image(image_path):
    """Returns a pygame image object with data loaded from 'image_path'
    """
    try:
        return pygame.image.load(image_path)
    except pygame.error:
        print("Could not load image", file=sys.stderr)
        return None


def draw_line(surface, color, offset, direction, scale):
    """Draws a line of color to the surface.
    Parameters are complex vectors representing offset, direction, and length
    """
    start = to_screen_coord(offset)
    end = to_screen_coord(offset+direction*scale)

    pygame.draw.aaline(surface, color, start, end)


def draw_selection_guides(screen, angle, selected):
    """Draws a pair of lines representing the current selection.
    Lines show the real and imaginary components of the polar representation
    """
    direction = unit_direction(angle)

    guide_start = selected.real * direction
    guide_end = selected.imag * perpendicular(direction)

    # Draws a line representing the real polar coordinate
    draw_line(screen, (0, 180, 0), 0, direction, 1000)
    # Draws a line representing the imaginary component of the polar coordinate
    draw_line(screen, (255, 0, 0), guide_start, guide_end, 1)


def main(background_path):
    # Init
    pygame.init()
    background = load_image(background_path)
    screen = pygame.display.set_mode((RENDER_RADIUS*2, RENDER_RADIUS*2))

    angle, selection = 0, 0
    path = []

    # Gameloop
    running, display_background = True, True
    while running:
        # Clears the screen
        screen.fill((0, 0, 0))

        # Draw to screen
        if display_background:
            draw_image(screen, background, (0, 0))

        draw_selection_guides(screen, angle, selection)
        for angle, point in path:
            direction = unit_direction(angle)

            start_guide = point.real * direction
            end_guide = point.imag * perpendicular(direction)
            screen.set_at(to_screen_coord(start_guide+end_guide), (255, 0, 0))

        # Events
        for event in pygame.event.get():
            if mouse_down_event(event):
                pos = from_screen_coord(event.pos)

                cursor_angle = math.atan2(pos.imag, pos.real) % (math.pi*2)
                if cursor_angle > angle:
                    angle = cursor_angle
                else:
                    angle += ANGLE_INC

                direction = unit_direction(angle)
                selection = convert_base(direction, pos)

                path.append((angle, selection))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    display_background = not display_background
                if event.key == pygame.K_RETURN:
                    # Save the whole path to out.p
                    with open("out.p", 'wb+') as out:
                        pickle.dump(path, out)

                    running = False

            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    print("Finshed")


if __name__ == "__main__":
    main(sys.argv[1])
