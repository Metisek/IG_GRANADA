from OpenGL.GL import *

class basic_object3D():
	def __init__(self):
		self.vertices = []

	def draw_point(self):
		glBegin(GL_POINTS)
		for vertex in self.vertices:
			glVertex3fv(vertex)
		glEnd()

