# lights.py
from OpenGL.GL import *
from OpenGL.GLU import gluNewQuadric, gluSphere
import numpy as np
from basic_object3d import basic_object3D

class Light(basic_object3D):
    def __init__(self,
                 position,
                 ambient=[0.0, 0.0, 0.0, 1.0],
                 diffuse=[1.0, 1.0, 1.0, 1.0],
                 specular=[1.0, 1.0, 1.0, 1.0],
                 brightness=1.0,
                 color=(1.0, 1.0, 1.0, 1.0), infinite=False):
        super().__init__()
        self.position = position
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.brightness = brightness
        self.infinite = infinite
        self.color = color


    def set_material(self, side, ambient, diffuse, specular, brightness):
        adjusted_diffuse = [c * brightness for c in diffuse]
        adjusted_specular = [c * brightness for c in specular]
        glMaterialfv(side, GL_AMBIENT, ambient)
        glMaterialfv(side, GL_DIFFUSE, adjusted_diffuse)
        glMaterialfv(side, GL_SPECULAR, adjusted_specular)