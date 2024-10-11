from OpenGL.GL import *

import common
from basic_object3d import basic_object3D

class object3D(basic_object3D):
    def __init__(self):
        super().__init__()
        self.triangles = []

    def draw_line(self):
        pass  # This will be implemented in derived classes

    def draw_fill(self):
        pass  # This will be implemented in derived classes

    def draw_chess(self):
        pass  # This will be implemented in derived classes
