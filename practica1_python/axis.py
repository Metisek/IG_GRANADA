from OpenGL.GL import *

from basic_object3d import basic_object3D
import common

DEFAULT_AXIS_SIZE = 5000

class axis(basic_object3D):
	def __init__(self, size = DEFAULT_AXIS_SIZE):
		super().__init__()
		self.vertices.append((-size, 0, 0))
		self.vertices.append((size, 0, 0))
		self.vertices.append((0, -size, 0))
		self.vertices.append((0, size, 0))
		self.vertices.append((0, 0, -size))
		self.vertices.append((0, 0, size))

	def draw_line(self):
		glLineWidth(1)
		glBegin(GL_LINES)
		glColor3fv(common.RED)
		glVertex3fv(self.vertices[0])
		glVertex3fv(self.vertices[1])
		glColor3fv(common.GREEN)
		glVertex3fv(self.vertices[2])
		glVertex3fv(self.vertices[3])
		glColor3fv(common.BLUE)
		glVertex3fv(self.vertices[4])
		glVertex3fv(self.vertices[5])
		glEnd()

