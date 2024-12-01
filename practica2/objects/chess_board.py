from object3d import object3D
from OpenGL.GL import *
import numpy as np
import common

class ChessBoard(object3D):
    def __init__(self):
        super().__init__()
        self.vertices = [
            [-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0]
        ]
        self.triangles = [
            [0, 1, 2], [2, 3, 0]
        ]
        self.texture_coords = [
            [0, 0], [1, 0], [1, 1], [0, 1]
        ]

    def draw_texture(self):
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            for vertex in triangle:
                glTexCoord2fv(self.texture_coords[vertex])
                glVertex3fv(self.vertices[vertex])
        glEnd()