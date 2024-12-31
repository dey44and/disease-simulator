import yaml

from engine.placeable import *


def load_scene_from_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    placeables = []
    for obj in data['placeables']:
        obj_type = obj['type']
        collision = obj['collision'] if 'collision' in obj else False
        if obj['geometry'] == 'rectangle':
            x, y, width, height = obj['x'], obj['y'], obj['width'], obj['height']
            color = tuple(obj['color'])
            placeables.append(Rectangle(obj_type, x, y, width, height, color, collision))
        elif obj['geometry'] == 'polygon':
            points = obj['points']
            color = tuple(obj['color'])
            placeables.append(Polygon(obj_type, points, color, collision))
        elif obj['geometry'] == 'circle':
            x, y, radius = obj['x'], obj['y'], obj['radius']
            color = tuple(obj['color'])
            placeables.append(Circle(obj_type, x, y, radius, color, collision))

    return placeables
