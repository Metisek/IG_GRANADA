# cylinder.py
from object3d import object3D
import math

class cylinder(object3D):
    def __init__(self, radius=1, height=2, num_segments=36):
        super().__init__()
        self.generate_cylinder(radius, height, num_segments)

    def generate_cylinder(self, radius, height, num_segments):
        angle_step = 2 * math.pi / num_segments

        # Podstawa i góra walca
        for i in range(num_segments):
            angle = i * angle_step
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            # Wierzchołki podstawy (y=0) i góry (y=height)
            self.vertices.append((x, 0, z))         # Podstawa
            self.vertices.append((x, height, z))   # Góra

        # Dodanie wierzchołka środka podstawy
        self.vertices.append((0, 0, 0))
        # Dodanie wierzchołka środka góry
        self.vertices.append((0, height, 0))

        # Tworzenie trójkątów bocznych walca
        for i in range(num_segments):
            self.triangles.append((i * 2, (i * 2 + 2) % (num_segments * 2), i * 2 + 1))
            self.triangles.append((i * 2 + 1, (i * 2 + 2) % (num_segments * 2), (i * 2 + 3) % (num_segments * 2)))

        # Tworzenie trójkątów podstawy (od środka do wierzchołków podstawy)
        center_bottom_index = num_segments * 2
        for i in range(num_segments):
            self.triangles.append((i * 2, (i * 2 + 2) % (num_segments * 2), center_bottom_index))

        # Tworzenie trójkątów góry (od środka do wierzchołków góry)
        center_top_index = num_segments * 2 + 1
        for i in range(num_segments):
            self.triangles.append((i * 2 + 1, center_top_index, (i * 2 + 3) % (num_segments * 2)))
