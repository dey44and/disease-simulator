import random


def random_subtile_in_rectangle(rect_placeable, map_density):
    """
    Generate a random subtile inside a rectangle based on a map density parameter.
    :param rect_placeable: Properties of the rectangle.
    :param map_density: Density of the standard tile.
    :return: A tuple that represents the random subtile.
    """
    sub_left = int(rect_placeable.x * map_density)
    sub_top = int(rect_placeable.y * map_density)
    sub_w = int(rect_placeable.width * map_density)
    sub_h = int(rect_placeable.height * map_density)

    gx = random.randint(sub_left, sub_left + sub_w - 1)
    gy = random.randint(sub_top, sub_top + sub_h - 1)
    return gx, gy