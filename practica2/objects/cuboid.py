# cuboid.py
from object3d import object3D

class Cuboid(object3D):
    def __init__(self, length=0.1, width=0.1, height=1.0):
        super().__init__()
        half_length = length / 2
        half_width = width / 2
        half_height = height / 2
        self.vertices.extend([
            (-half_length, -half_width, -half_height),
            ( half_length, -half_width, -half_height),
            ( half_length,  half_width, -half_height),
            (-half_length,  half_width, -half_height),
            (-half_length, -half_width,  half_height),
            ( half_length, -half_width,  half_height),
            ( half_length,  half_width,  half_height),
            (-half_length,  half_width,  half_height),
        ])

        # Define triangles for fill mode
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