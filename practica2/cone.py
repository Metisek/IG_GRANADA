# cone.py
from object3d import object3D
import math

class cone(object3D):
    def __init__(self, radius=1, height=2, num_segments=36):
        super().__init__()
        self.generate_cone(radius, height, num_segments)

    def generate_cone(self, radius, height, num_segments):
        angle_step = 2 * math.pi / num_segments

        for i in range(num_segments):
            angle = i * angle_step
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            self.vertices.append((x, 0, z))

        self.vertices.append((0, height, 0))

        for i in range(num_segments):
            self.triangles.append((i, (i + 1) % num_segments, num_segments))

        for i in range(num_segments):
            self.triangles.append((i, (i + 1) % num_segments, num_segments + 1))

        self.vertices.append((0, 0, 0))

        for i in range(num_segments):
            self.triangles.append((i, (i + 1) % num_segments, num_segments))
