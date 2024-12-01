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
        # Apply the material properties using OpenGL functions
        glMaterialfv(GL_FRONT, GL_AMBIENT, self.ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.specular)
        glMaterialf(GL_FRONT, GL_SHININESS, self.shininess)
        glColor4fv(self.color)