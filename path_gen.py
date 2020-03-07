"""
A tool for generating a path from an image
"""

import sys
from functools import partial
from itertools import tee

from PIL import Image

BIG_NUMBER = (1 << 32)
SCAN_OFFSETS = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def add(v1, v2):
    return (v1[0]+v2[0], v1[1]+v2[1])


def get_l(data, point):
    try:
        return data[point[1]][point[0]]
    except IndexError:
        # Default value used, no need for bound checking
        print("Index get error")
        return BIG_NUMBER


def set_l(data, point, l):
    try:
        data[point[1]][point[0]] = l
    except IndexError:
        # Out of bounds, ignore write
        print("Index set error")
        pass


def get_surroundings(data, point):
    return map(
        partial(add, point),
        SCAN_OFFSETS
    )


def get_empty_surroundings(data, point):
    return filter(
        lambda pos: get_l(data, pos) is None,
        get_surroundings(data, point)
    )


def is_black(color):
    return color[0] != 255 and color[1] != 255 and color[2] != 255


def get_image_data(image_path):
    im = Image.open(image_path)

    width, height = im.size
    pixels = im.load()

    data = []
    for y in range(height):
        row = []
        for x in range(width):
            if is_black(pixels[x, y]):
                row.append(None)
            else:
                row.append(BIG_NUMBER)
        data.append(row)
    return data


def gen_start_end(data):
    CENTER = (len(data[0])//2, len(data)//2)
    # Clear center line to prevent 0 length path
    # Also find max and min x+y
    for n in range(CENTER[0]):
        point = add(CENTER, (n, 0))
        set_l(data, point, BIG_NUMBER)

        if get_l(data, add(point, (0, -1))) is None:
            start = add(point, (0, -1))
        if get_l(data, add(point, (0, 1))) is None:
            end = add(point, (0, 1))
    return start, end


def fill_image_data(data, start, end):
    set_l(data, end, 0)

    next_queue = []
    queue = [(0, end)]
    while queue:
        while queue:
            cost, coord = queue.pop()
            if coord == start:
                return

            for point in get_empty_surroundings(data, coord):
                set_l(data, point, cost+1)
                next_queue.append((cost+1, point))

        queue = next_queue
        next_queue = []


def shortest_path(data, start, end):
    path = [start]
    while path[-1] != end:
        s1, s2 = tee(get_surroundings(data, path[-1]))
        path.append(min(zip(
            map(
                partial(get_l, data),
                s1
            ), s2
        ))[1])
    return path


def show_path(path, size):
    im = Image.new('RGB', size)
    data = im.load()
    for pixel in path:
        data[pixel] = (255, 255, 255)
    im.show()


if __name__ == "__main__":
    data = get_image_data(sys.argv[1])
    start, end = gen_start_end(data)
    fill_image_data(data, start, end)

    path = shortest_path(data, start, end)
    show_path(path, (len(data[0]), len(data)))
