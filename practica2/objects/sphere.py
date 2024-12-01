# sphere.py
from object3d import object3D
import math

class sphere(object3D):
    def __init__(self, radius=1, num_segments=36):
        super().__init__()
        self.generate_sphere(radius, num_segments)

    def generate_sphere(self, radius, num_segments):
        # Wierzchołki kuli
        for i in range(num_segments):
            theta = i * math.pi / num_segments
            for j in range(num_segments):
                phi = j * 2 * math.pi / num_segments
                x = radius * math.sin(theta) * math.cos(phi)
                y = radius * math.cos(theta)
                z = -radius * math.sin(theta) * math.sin(phi)
                self.vertices.append((x, y, z))

        # Dodanie wierzchołka na górze kuli (biegun północny)
        self.vertices.append((0, radius, 0))

        # Dodanie wierzchołka na dole kuli (biegun południowy)
        self.vertices.append((0, -radius, 0))

        # Tworzenie trójkątów dla powierzchni kuli
        for i in range(num_segments - 1):
            for j in range(num_segments):
                self.triangles.append((
                    i * num_segments + j,
                    i * num_segments + (j + 1) % num_segments,
                    (i + 1) * num_segments + j
                ))
                self.triangles.append((
                    (i + 1) * num_segments + j,
                    i * num_segments + (j + 1) % num_segments,
                    (i + 1) * num_segments + (j + 1) % num_segments
                ))

        # Tworzenie trójkątów dla biegunu górnego
        north_pole_index = num_segments * num_segments
        for j in range(num_segments):
            self.triangles.append((
                j,
                (j + 1) % num_segments,
                north_pole_index
            ))

        # Tworzenie trójkątów dla biegunu dolnego
        south_pole_index = num_segments * num_segments + 1
        for j in range(num_segments):
            self.triangles.append((
                (num_segments - 1) * num_segments + j,
                (num_segments - 1) * num_segments + (j + 1) % num_segments,
                south_pole_index
            ))
