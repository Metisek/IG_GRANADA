# hierarchial_model.py
from OpenGL.GL import *
import math
from objects.cuboid import Cuboid
from object3d import object3D
from materials import OpenGLMaterial

class HierarchicalModel:
    def __init__(self):
        self.components = []
        self.selected_triangle = None

    def draw(self, draw_mode, material: OpenGLMaterial = None):
        for component in self.components:
            glPushMatrix()
            component.draw(draw_mode, material, self.selected_triangle)
            glPopMatrix()

    def draw_with_ids(self):
        iteration = 0
        for component in self.components:
            iteration = component.draw_with_ids(iteration)