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

    def apply_light(self, light_id):
        glEnable(GL_LIGHTING)
        glEnable(light_id)

        position = np.array(self.position + [0.0 if self.infinite else 1.0], dtype=np.float32)
        glLightfv(light_id, GL_POSITION, position)
        glLightfv(light_id, GL_AMBIENT, self.ambient)
        glLightfv(light_id, GL_DIFFUSE, [c * self.brightness for c in self.diffuse])
        glLightfv(light_id, GL_SPECULAR, [c * self.brightness for c in self.specular])
        # Draw light as a circle in space
        color = self.color
        if color == (1.0, 1.0, 1.0, 1.0):
            color = (0.0, 0.0, 0.0, 1.0)
        glMaterialfv(GL_FRONT, GL_EMISSION, color)
        glPushMatrix()
        glTranslatef(*self.position)
        quadric = gluNewQuadric()
        gluSphere(quadric, 0.05, 16, 16)  # Small sphere with radius 0.05
        glPopMatrix()
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])

    def set_material(self, side, ambient, diffuse, specular, brightness):
        adjusted_diffuse = [c * brightness for c in diffuse]
        adjusted_specular = [c * brightness for c in specular]
        glMaterialfv(side, GL_AMBIENT, ambient)
        glMaterialfv(side, GL_DIFFUSE, adjusted_diffuse)
        glMaterialfv(side, GL_SPECULAR, adjusted_specular)