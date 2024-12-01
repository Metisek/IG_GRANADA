# materials.py
from OpenGL.GL import *

class OpenGLMaterial:
    def __init__(self, name, ambient, diffuse, specular, shininess, color):
        self.name = name
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.color = color

    def apply(self):
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.specular)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.shininess)
        glColor4fv(self.color)

