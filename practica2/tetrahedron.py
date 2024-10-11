from object3d import object3D
from OpenGL.GL import *
import common

class tetrahedron(object3D):
    def __init__(self, size=1):
        super().__init__()
        self.vertices.append((-size / 2, -size / 2, -size / 2))
        self.vertices.append((0, -size / 2, size / 2))
        self.vertices.append((size / 2, -size / 2, -size / 2))
        self.vertices.append((0, size / 2, 0))

        self.triangles.append((0, 1, 3))
        self.triangles.append((1, 2, 3))
        self.triangles.append((2, 0, 3))
        self.triangles.append((0, 2, 1))

    def draw_line(self):
        glBegin(GL_LINES)
        for triangle in self.triangles:
            for vertex_index in triangle:
                glVertex3fv(self.vertices[vertex_index])
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




