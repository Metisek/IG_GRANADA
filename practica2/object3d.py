# object3d.py
from OpenGL.GL import (
    glBegin, glEnd, glVertex3fv, glColor3fv, glTexCoord2fv, glNormal3fv,
    glEnable, glDisable, glBindTexture, glShadeModel, GL_LINES, GL_TRIANGLES,
    GL_FLAT, GL_SMOOTH, GL_TEXTURE_2D, GL_LIGHTING, GL_LIGHT0, GL_MAX_LIGHTS,
    glColor3f
)
import numpy as np
import common
from basic_object3d import basic_object3D
from lights import Light
from materials import OpenGLMaterial


class object3D(basic_object3D):
    def __init__(self):
        super().__init__()
        self.triangles = []
        self.normals = []
        self.vertex_normals = []
        self.texture_coords = []
        self.selected_triangle = None
        self.texture_id = None

    def draw_line(self):
        glBegin(GL_LINES)
        for triangle in self.triangles:
            glVertex3fv(self.vertices[triangle[0]])
            glVertex3fv(self.vertices[triangle[1]])
            glVertex3fv(self.vertices[triangle[1]])
            glVertex3fv(self.vertices[triangle[2]])
            glVertex3fv(self.vertices[triangle[2]])
            glVertex3fv(self.vertices[triangle[0]])
        glEnd()

    def draw_fill(self):
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            if i == self.selected_triangle:
                glColor3fv(common.YELLOW)
            else:
                glColor3fv(common.BLUE)
            for vertex_index in triangle:
                glVertex3fv(self.vertices[vertex_index])
        glEnd()

    def draw_chess(self):
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            color = common.RED if i % 2 == 0 else common.GREEN
            glColor3fv(color)
            for vertex_index in triangle:
                glVertex3fv(self.vertices[vertex_index])
        glEnd()

    def calculate_normals(self):
        self.normals = np.zeros((len(self.vertices), 3), dtype=np.float32)  # Initialize with float32
        for triangle in self.triangles:
            v0, v1, v2 = [np.array(self.vertices[i], dtype=np.float32) for i in triangle]  # Ensure vertices are float32
            normal = np.cross(v1 - v0, v2 - v0)
            normal /= np.linalg.norm(normal)
            for i in triangle:
                self.normals[i] += normal
        self.normals = [normal / np.linalg.norm(normal) for normal in self.normals]

    def calculate_face_normals(self):
        self.normals = []
        for triangle in self.triangles:
            v0 = np.array(self.vertices[triangle[0]], dtype=np.float32)
            v1 = np.array(self.vertices[triangle[1]], dtype=np.float32)
            v2 = np.array(self.vertices[triangle[2]], dtype=np.float32)
            normal = np.cross(v1 - v0, v2 - v0)
            normal /= np.linalg.norm(normal)
            self.normals.append(normal)

    def calculate_vertex_normals(self):
        self.vertex_normals = [np.zeros(3, dtype=np.float32) for _ in range(len(self.vertices))]
        for triangle in self.triangles:
            v0, v1, v2 = [np.array(self.vertices[i], dtype=np.float32) for i in triangle]
            normal = np.cross(v1 - v0, v2 - v0)
            normal /= np.linalg.norm(normal)
            for i in triangle:
                self.vertex_normals[i] += normal
        self.vertex_normals = [normal / np.linalg.norm(normal) for normal in self.vertex_normals]

    def apply_lights(self, lights: list[Light]):
        glDisable(GL_LIGHTING)
        for i in range(8):
            glDisable(GL_LIGHT0 + i)
        for i, light in enumerate(lights):
            if i < GL_MAX_LIGHTS:
                light.apply_light(GL_LIGHT0 + i)
        if lights:
            glEnable(GL_LIGHTING)

    def draw_flat_shaded(self, lights: list[Light], material: OpenGLMaterial):
        self.calculate_face_normals()
        material.apply()
        self.apply_lights(lights)
        glShadeModel(GL_FLAT)
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            glNormal3fv(self.normals[i])
            glVertex3fv(self.vertices[triangle[0]])
            glVertex3fv(self.vertices[triangle[1]])
            glVertex3fv(self.vertices[triangle[2]])
        glEnd()
        glDisable(GL_LIGHTING)

    def draw_gouraud_shaded(self, lights: list[Light], material: OpenGLMaterial):
        self.calculate_vertex_normals()
        self.apply_lights(lights)
        material.apply()
        glShadeModel(GL_SMOOTH)
        glBegin(GL_TRIANGLES)
        for triangle in self.triangles:
            glNormal3fv(self.vertex_normals[triangle[0]])
            glVertex3fv(self.vertices[triangle[0]])
            glNormal3fv(self.vertex_normals[triangle[1]])
            glVertex3fv(self.vertices[triangle[1]])
            glNormal3fv(self.vertex_normals[triangle[2]])
            glVertex3fv(self.vertices[triangle[2]])
        glEnd()
        glDisable(GL_LIGHTING)

    def draw_unlit_texture(self, material: OpenGLMaterial):
        if not self.texture_coords or len(self.texture_coords) != len(self.vertices):
            print("Error: Texture coordinates are not set correctly.")
            return

        if not hasattr(self, 'texture_id') or self.texture_id is None:
            print("Error: Texture is not loaded.")
            return

        material.apply()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glDisable(GL_LIGHTING)  # Wyłączenie oświetlenia
        glColor3f(1.0, 1.0, 1.0)  # Neutralny kolor (biały)

        glBegin(GL_TRIANGLES)
        for triangle in self.triangles:
            for vertex in triangle:
                glTexCoord2fv(self.texture_coords[vertex])
                glVertex3fv(self.vertices[vertex])
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)  # Odłączenie tekstury


    def draw_texture_flat_shaded(self, lights: list[Light], material: OpenGLMaterial):
        self.calculate_face_normals()  # Use face normals for flat shading
        material.apply()
        self.apply_lights(lights)
        glShadeModel(GL_FLAT)

        if not self.texture_id:
            print("Error: Texture not loaded.")
            return

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glColor3f(1.0, 1.0, 1.0)  # Neutral color (white)

        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            glNormal3fv(self.normals[i])  # Use face normal
            for vertex in triangle:
                glTexCoord2fv(self.texture_coords[vertex])
                glVertex3fv(self.vertices[vertex])
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        glEnable(GL_LIGHTING)


    def draw_texture_gouraud_shaded(self, lights: list[Light], material: OpenGLMaterial):
        self.calculate_vertex_normals()  # Use vertex normals for Gouraud shading
        material.apply()
        self.apply_lights(lights)
        glShadeModel(GL_SMOOTH)

        if not self.texture_id:
            print("Error: Texture not loaded.")
            return

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        glColor3f(1.0, 1.0, 1.0)  # Neutral color (white)

        glBegin(GL_TRIANGLES)
        for triangle in self.triangles:
            for vertex in triangle:
                glTexCoord2fv(self.texture_coords[vertex])
                glNormal3fv(self.vertex_normals[vertex])  # Use vertex normal
                glVertex3fv(self.vertices[vertex])
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        glEnable(GL_LIGHTING)

    def draw_with_ids(self):
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            color = self.int_to_color(i)
            glColor3fv(color)
            for vertex_index in triangle:
                glVertex3fv(self.vertices[vertex_index])
        glEnd()

    def int_to_color(self, i):
        r = (i & 0xFF0000) >> 16
        g = (i & 0x00FF00) >> 8
        b = (i & 0x0000FF)
        return [r / 255.0, g / 255.0, b / 255.0]

