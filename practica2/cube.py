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

    def draw_line(self):
        glBegin(GL_LINES)
        for i in range(4):  # Front face
            glVertex3fv(self.vertices[i])
            glVertex3fv(self.vertices[(i + 1) % 4])
        for i in range(4, 8):  # Back face
            glVertex3fv(self.vertices[i])
            glVertex3fv(self.vertices[(i + 1) % 4 + 4])
        for i in range(4):  # Connecting edges
            glVertex3fv(self.vertices[i])
            glVertex3fv(self.vertices[i + 4])
        glEnd()

    def draw_fill(self):
        glBegin(GL_TRIANGLES)
        for triangle in self.triangles:
            for vertex_index in triangle:
                glVertex3fv(self.vertices[vertex_index])
        glEnd()

    def draw_chess(self):
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            color = common.RED if i % 2 == 0 else common.GREEN
            glColor3fv(color)
            for vertex_index in triangle:
                glVertex3fv(self.vertices[vertex_index])
        glEnd()
