# file_ply.py
import sys
from OpenGL.GL import *
import common
from object3d import object3D
import math

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


class RevolutionObject(object3D):
    def __init__(self, profile_points, num_segments=36):
        super().__init__()
        self.generate_revolution_object(profile_points, num_segments)

    def generate_revolution_object(self, profile_points, num_segments):
        angle_step = 2 * math.pi / num_segments
        vertices = []
        triangles = []

        # Tworzenie punktów przez obrót
        for i in range(num_segments):
            angle = i * angle_step
            for x, y in profile_points:
                new_x = x * math.cos(angle)
                new_z = -x * math.sin(angle)
                vertices.append((new_x, y, new_z))

        # Tworzenie trójkątów
        num_profile_points = len(profile_points)
        for i in range(num_segments):
            for j in range(num_profile_points - 1):
                p1 = i * num_profile_points + j
                p2 = ((i + 1) % num_segments) * num_profile_points + j
                p3 = p1 + 1
                p4 = p2 + 1

                # Dodaj trójkąty, jeśli nie są zdegenerowane
                if p1 != p2 and p1 != p3 and p2 != p3:
                    triangles.append((p1, p2, p3))
                if p2 != p3 and p2 != p4 and p3 != p4:
                    triangles.append((p2, p4, p3))

        self.vertices = vertices
        self.triangles = triangles
