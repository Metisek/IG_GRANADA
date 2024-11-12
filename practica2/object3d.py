# object3D.py
from OpenGL.GL import *

import common
from basic_object3d import basic_object3D
class object3D(basic_object3D):
    def __init__(self):
        super().__init__()
        self.triangles = []

    def draw_line(self):
        glBegin(GL_LINES)
        for triangle in self.triangles:
            glVertex3fv(self.vertices[triangle[0]])
            glVertex3fv(self.vertices[triangle[1]])
            glVertex3fv(self.vertices[triangle[1]])
            glVertex3fv(self.vertices[triangle[2]])
            glVertex3fv(self.vertices[triangle[2]])
            glVertex3fv(self.vertices[triangle[0]])
        glEnd()

    def draw_fill(self):
        glBegin(GL_TRIANGLES)
        for triangle in self.triangles:
            glVertex3fv(self.vertices[triangle[0]])
            glVertex3fv(self.vertices[triangle[1]])
            glVertex3fv(self.vertices[triangle[2]])
        glEnd()

    def draw_chess(self):
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            color = common.RED if i % 2 == 0 else common.GREEN
            glColor3fv(color)
            for vertex_index in triangle:
                glVertex3fv(self.vertices[vertex_index])
        glEnd()
