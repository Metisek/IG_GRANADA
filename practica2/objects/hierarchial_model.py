# hierarchial_model.py
from OpenGL.GL import *
import math
from objects.cuboid import Cuboid
from object3d import object3D
from materials import OpenGLMaterial

class HierarchicalModel:
    def __init__(self):
        self.components = []
        self.components_indexes_search = {}

    def draw(self, draw_mode, lights=[], material: OpenGLMaterial = None):
        for component in self.components:
            glPushMatrix()
            component.draw(draw_mode, lights, material)
            glPopMatrix()