from object3d import object3D
from OpenGL.GL import *
import numpy as np
import common

class ChessBoard(object3D):
    def __init__(self):
        super().__init__()
        self.vertices = [
            [-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0],  # bottom vertices
            [-1, -1, 0.1], [1, -1, 0.1], [1, 1, 0.1], [-1, 1, 0.1]  # top vertices
        ]

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

        self.texture_coords = [
            [0, 0], [1, 0], [1, 1], [0, 1],
            [0, 0], [1, 0], [1, 1], [0, 1]
        ]