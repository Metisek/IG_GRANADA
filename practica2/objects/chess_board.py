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
        self.triangles = [
            [0, 1, 2], [2, 3, 0],  # bottom face
            [4, 5, 6], [6, 7, 4],  # top face
            [0, 1, 5], [5, 4, 0],  # side face 1
            [1, 2, 6], [6, 5, 1],  # side face 2
            [2, 3, 7], [7, 6, 2],  # side face 3
            [3, 0, 4], [4, 7, 3]   # side face 4
        ]
        self.texture_coords = [
            [0, 0], [1, 0], [1, 1], [0, 1],
            [0, 0], [1, 0], [1, 1], [0, 1]
        ]

        def draw_texture(self):
            glBegin(GL_TRIANGLES)
            for i, triangle in enumerate(self.triangles[:4]):  # Only texture the top and bottom faces
                for vertex in triangle:
                    glTexCoord2fv(self.texture_coords[vertex])
                    glVertex3fv(self.vertices[vertex])
            glEnd()

        def draw(self):
            glBegin(GL_TRIANGLES)
            for triangle in self.triangles:
                for vertex in triangle:
                    glVertex3fv(self.vertices[vertex])
            glEnd()