# common.py
RED = (1, 0, 0)
GREEN = (0, 1, 0)
BLUE = (0, 0, 1)
CIAN = (0, 1, 1)
MAGENTA = (1, 0, 1)
YELLOW = (1, 1, 0)
BLACK = (0, 0, 0)
WHITE = (1, 1, 1)

def is_dark(color):
    return (color[0] * 0.299 + color[1] * 0.587 + color[2] * 0.114) < 0.5

DARK_YELLOW = (0.5, 0.5, 0)

DEFAULT_MATERIAL = {
    'name': 'default',
    'ambient': (0.1, 0.1, 0.1, 1.0),
    'diffuse': (0.7, 0.7, 0.7, 1.0),
    'specular': (0.9, 0.9, 0.9, 1.0),
    'shininess': 100.0,
    'color': (0.5, 0.5, 0.5, 1.0),
}
