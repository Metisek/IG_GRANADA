# cube.py
from object3d import object3D
from OpenGL.GL import *
import common

class cube(object3D):
    def __init__(self, size=1):
        super().__init__()
        half_size = size / 2
        self.vertices.extend([
            (-half_size, -half_size, -half_size),
            ( half_size, -half_size, -half_size),
            ( half_size,  half_size, -half_size),
            (-half_size,  half_size, -half_size),
            (-half_size, -half_size,  half_size),
            ( half_size, -half_size,  half_size),
            ( half_size,  half_size,  half_size),
            (-half_size,  half_size,  half_size),
        ])

        # Define triangles for fill mode
        self.triangles.extend([
            (0, 1, 2), (0, 2, 3),
            (4, 5, 6), (4, 6, 7),
            (0, 1, 5), (0, 5, 4),
            (2, 3, 7), (2, 7, 6),
            (0, 3, 7), (0, 7, 4),
            (1, 2, 6), (1, 6, 5),
        ])

