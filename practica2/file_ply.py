import sys
from OpenGL.GL import *
import common
from object3d import object3D

def read_ply(file_name):
    with open(file_name, mode='r', encoding='utf-8') as file:
        lines = file.readlines()

        if lines[0].strip() != 'ply':
            print('Error with ply file')
            sys.exit(1)

        pos_line = 1
        num_vertices = 0
        num_triangles = 0

        # Parse header
        while pos_line < len(lines):
            line = lines[pos_line].strip()
            tokens = line.split()

            if tokens[0] == 'element':
                if tokens[1] == 'vertex':
                    num_vertices = int(tokens[2])
                elif tokens[1] == 'face':
                    num_triangles = int(tokens[2])
            elif tokens[0] == 'end_header':
                pos_line += 1
                break
            pos_line += 1

        # Read vertices
        vertices = []
        for _ in range(num_vertices):
            if pos_line >= len(lines):
                print('Error: Not enough vertex data')
                sys.exit(1)
            line = lines[pos_line].strip()
            tokens = line.split()
            if len(tokens) < 3:
                print('Error: Invalid vertex format')
                sys.exit(1)
            x, y, z = float(tokens[0]), float(tokens[1]), float(tokens[2])
            vertices.append((x, y, z))
            pos_line += 1

        # Read triangles
        triangles = []
        for _ in range(num_triangles):
            if pos_line >= len(lines):
                print('Error: Not enough face data')
                sys.exit(1)
            line = lines[pos_line].strip()
            tokens = line.split()
            if tokens[0] != '3':
                print('Error: Face is not a triangle')
                sys.exit(1)
            i, j, k = int(tokens[1]), int(tokens[2]), int(tokens[3])
            triangles.append((i, j, k))
            pos_line += 1

        return vertices, triangles

class PLYObject(object3D):
    def __init__(self, file_name):
        super().__init__()
        self.vertices, self.triangles = read_ply(file_name)

    def draw_line(self):
        glBegin(GL_LINES)
        glColor3fv(common.CIAN)  # Możesz wybrać inny kolor
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
        glColor3fv(common.YELLOW)  # Kolor wypełnienia
        for triangle in self.triangles:
            glVertex3fv(self.vertices[triangle[0]])
            glVertex3fv(self.vertices[triangle[1]])
            glVertex3fv(self.vertices[triangle[2]])
        glEnd()

    def draw_chess(self):
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.triangles):
            color = common.RED if i % 2 == 0 else common.GREEN
            glColor3fv(color)
            glVertex3fv(self.vertices[triangle[0]])
            glVertex3fv(self.vertices[triangle[1]])
            glVertex3fv(self.vertices[triangle[2]])
        glEnd()
