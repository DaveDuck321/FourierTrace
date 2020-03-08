"""
A tool for generating a path from an image
"""

import utils
from path_tool import PathCreate

import sys
import pickle
from functools import partial
from PIL import Image

BLANK_COLOR = (255, 255, 255)
START_COLOR = (255, 0, 0)
END_COLOR = (0, 0, 255)

BIG_NUMBER = (1 << 32)
SCAN_OFFSETS = [(0, 1), (0, -1), (1, 0), (-1, 0)]


class ImageData():
    """A container for storing the data extracted from the path image
    """
    def __init__(self, size):
        self.start, self.end = None, None
        self.size = size
        self.data = [[BIG_NUMBER]*size[1] for _ in range(size[0])]

    def __setitem__(self, index, value):
        try:
            self.data[index[1]][index[0]] = value
        except IndexError:
            # Out of bounds, ignore write
            # print("Index set error")
            pass

    def __getitem__(self, index):
        try:
            return self.data[index[1]][index[0]]
        except IndexError:
            # Default value used, no need for bound checking
            return BIG_NUMBER


def get_surroundings(data, point):
    return map(
        partial(utils.add, point),
        SCAN_OFFSETS
    )


def filter_surroundings(data, point, condition=(lambda x: x is not None)):
    return filter(
        lambda pos: condition(data[pos]),
        get_surroundings(data, point)
    )


def is_color(c1, c2, delta=50):
    return (abs(c1[0]-c2[0]) < delta) and (
        abs(c1[1]-c2[1]) < delta) and (
            abs(c1[2]-c2[2]) < delta)


def get_image_data(image_path):
    im = Image.open(image_path).convert("RGB")

    width, height = im.size
    pixels = im.load()
    data = ImageData(im.size)
    for y in range(height):
        for x in range(width):
            if is_color(pixels[x, y], BLANK_COLOR):
                continue

            data[x, y] = None
            if is_color(pixels[x, y], START_COLOR):
                data.start = (x, y)
                print(f"Path start: {data.start}")
            if is_color(pixels[x, y], END_COLOR):
                data.end = (x, y)
                print(f"Path end: {data.end}")
    return data


def fill_image_data(data):
    data[data.end] = 0

    next_queue = []
    queue = [(0, data.end)]
    while queue:
        while queue:
            cost, coord = queue.pop()
            if coord == data.start:
                return

            for point in filter_surroundings(data, coord, lambda x: x is None):
                data[point] = cost+1
                next_queue.append((cost+1, point))

        queue = next_queue
        next_queue = []


def shortest_path(data):
    path = [data.start]
    while path[-1] != data.end:
        next_point = min(
            (data[point], point)
            for point in filter_surroundings(data, path[-1])
        )
        path.append(next_point[1])

    return path


def show_path(path, size):
    im = Image.new('RGB', size)
    data = im.load()
    for pixel in path:
        data[pixel] = (255, 255, 255)
    im.show()


def save_path(path, size, file_path):
    creator = PathCreate()
    coord_convert = partial(utils.from_vector_coord, (size[0]//2, size[1]//2))

    for pixel in path[::-1]:
        creator.add_point(coord_convert(pixel))

    with open(file_path, 'wb+') as file:
        pickle.dump(creator.path, file)


if __name__ == "__main__":
    data = get_image_data(sys.argv[1])
    fill_image_data(data)

    path = shortest_path(data)
    show_path(path, data.size)
    save_path(path, data.size, "out.p")
