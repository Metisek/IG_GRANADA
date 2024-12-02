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
