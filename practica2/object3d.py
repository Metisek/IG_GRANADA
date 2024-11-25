# object3D.py
from OpenGL.GL import *
import numpy as np
import common
from basic_object3d import basic_object3D

class object3D(basic_object3D):
    def __init__(self):
        super().__init__()
        self.triangles = []
        self.normals = []
        self.vertex_normals = []
        self.texture_coords = []

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

    def compute_normals(self):
        self.normals = []
        for triangle in self.triangles:
            p0, p1, p2 = [self.vertices[i] for i in triangle]
            a = np.subtract(p1, p0)
            b = np.subtract(p2, p0)
            normal = np.cross(a, b)
            normal = normal / np.linalg.norm(normal)
            self.normals.append(normal)

        self.vertex_normals = [np.zeros(3) for _ in self.vertices]
        for i, triangle in enumerate(self.triangles):
            for vertex in triangle:
                self.vertex_normals[vertex] += self.normals[i]
        self.vertex_normals = [n / np.linalg.norm(n) for n in self.vertex_normals]

    def set_material(self, ambient, diffuse, specular, shininess):
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, specular)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, shininess)

    def set_lighting(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)

        light0_position = [1.0, 1.0, 1.0, 0.0]
        light0_diffuse = [1.0, 1.0, 1.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light0_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)

        light1_position = [0.0, 1.0, 0.0, 1.0]
        light1_diffuse = [1.0, 0.0, 1.0, 1.0]
        glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)

    def draw_flat_shading(self):
        glShadeModel(GL_FLAT)
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            glNormal3fv(self.normals[i])
            for vertex in triangle:
                glVertex3fv(self.vertices[vertex])
        glEnd()

    def draw_gouraud_shading(self):
        glShadeModel(GL_SMOOTH)
        glBegin(GL_TRIANGLES)
        for triangle in self.triangles:
            for vertex in triangle:
                glNormal3fv(self.vertex_normals[vertex])
                glVertex3fv(self.vertices[vertex])
        glEnd()

    def draw_texture(self):
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            for vertex in triangle:
                glTexCoord2fv(self.texture_coords[vertex])
                glVertex3fv(self.vertices[vertex])
        glEnd()
        glDisable(GL_TEXTURE_2D)