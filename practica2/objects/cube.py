# cube.py
from object3d import object3D
from OpenGL.GL import *
import common

class cube(object3D):
    def __init__(self, size=1):
        super().__init__()
        half_size = size / 2
        # Wierzchołki sześcianu
        self.vertices.extend([
            (-half_size, -half_size, -half_size),  # 0
            ( half_size, -half_size, -half_size),  # 1
            ( half_size,  half_size, -half_size),  # 2
            (-half_size,  half_size, -half_size),  # 3
            (-half_size, -half_size,  half_size),  # 4
            ( half_size, -half_size,  half_size),  # 5
            ( half_size,  half_size,  half_size),  # 6
            (-half_size,  half_size,  half_size),  # 7
        ])

        # Trójkąty sześcianu (korekta orientacji wierzchołków)
        self.triangles.extend([
            # Przednia ściana (z -)
            (0, 2, 1), (0, 3, 2),
            # Tylna ściana (z +)
            (4, 5, 6), (4, 6, 7),
            # Prawa ściana (x +)
            (1, 6, 5), (1, 2, 6),
            # Lewa ściana (x -)
            (0, 7, 3), (0, 4, 7),
            # Górna ściana (y +)
            (3, 6, 2), (3, 7, 6),
            # Dolna ściana (y -)
            (0, 5, 4), (0, 1, 5),
        ])
