from OpenGL.GL import *
import numpy as np
import common
from basic_object3d import basic_object3D

class Light(basic_object3D):
    def __init__(self,
                 position,
                 ambient=[0.0, 0.0, 0.0, 1.0],
                 diffuse=[1.0, 1.0, 1.0, 1.0],
                 specular=[1.0, 1.0, 1.0, 1.0],
                 shininess=40.0,
                 color=(1.0, 1.0, 1.0, 1.0), infinite=False):
        super().__init__()
        self.position = position
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.color = color
        self.infinite = infinite

    def apply_light(self, light_id):
        glEnable(GL_LIGHTING)
        glEnable(light_id)

        if self.infinite:
            position = np.array([self.position[0], self.position[1], self.position[2], 0.0], dtype=np.float32)
        else:
            position = np.array([self.position[0], self.position[1], self.position[2], 1.0], dtype=np.float32)

        glLightfv(light_id, GL_POSITION, position)
        glLightfv(light_id, GL_AMBIENT, self.ambient)
        glLightfv(light_id, GL_DIFFUSE, self.diffuse)
        glLightfv(light_id, GL_SPECULAR, self.specular)
        glLightfv(light_id, GL_DIFFUSE, self.color)

    def set_material(self, side, ambient, diffuse, specular, shininess):
        glMaterialfv(side, GL_AMBIENT, ambient)
        glMaterialfv(side, GL_DIFFUSE, diffuse)
        glMaterialfv(side, GL_SPECULAR, specular)
        glMaterialf(side, GL_SHININESS, shininess)

    def enable_flat_shading(self):
        glShadeModel(GL_FLAT)

    def enable_smooth_shading(self):
        glShadeModel(GL_SMOOTH)