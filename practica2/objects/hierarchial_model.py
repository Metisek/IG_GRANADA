# hierarchial_model.py
from OpenGL.GL import *
import math
from objects.cuboid import Cuboid
from object3d import object3D
from materials import OpenGLMaterial

class HierarchicalModel:
    def __init__(self):
        self.components = []

    def draw(self, draw_mode, lights=[], material: OpenGLMaterial = None):
        for component in self.components:
            glPushMatrix()
            component.draw(draw_mode, lights, material)
            glPopMatrix()

class Component(object3D):
    def __init__(self, length, width=0.1, height=0.1, depth=1.0,
                 angle_pitch=0, angle_yaw=0, angle_roll=0,
                 rotation_axis_pitch=False, rotation_axis_yaw=False, rotation_axis_roll=False,
                 limit_pitch=None, limit_yaw=None, limit_roll=None,
                 limit_speed_pitch=5, limit_speed_yaw=5, limit_speed_roll=5,
                 speed_pitch=1, speed_yaw=1, speed_roll=1,
                 offset_x=0, offset_y=0, offset_z=0,
                 origin_x=0, origin_y=0, origin_z=0):
        self.length = length
        self.width = width
        self.height = height
        self.depth = depth

        self.angle_pitch = angle_pitch
        self.angle_yaw = angle_yaw
        self.angle_roll = angle_roll

        self.rotation_axis_pitch = rotation_axis_pitch
        self.rotation_axis_yaw = rotation_axis_yaw
        self.rotation_axis_roll = rotation_axis_roll

        self.limit_pitch = limit_pitch
        self.limit_yaw = limit_yaw
        self.limit_roll = limit_roll

        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z

        self.origin_x = origin_x
        self.origin_y = origin_y
        self.origin_z = origin_z

        self.limit_speed_pitch = limit_speed_pitch
        self.limit_speed_yaw = limit_speed_yaw
        self.limit_speed_roll = limit_speed_roll

        self.speed_pitch = speed_pitch
        self.speed_yaw = speed_yaw
        self.speed_roll = speed_roll

        self.cuboid = Cuboid(self.length, self.width, self.height, self.depth,
                     self.angle_pitch, self.angle_yaw, self.angle_roll,
                     self.rotation_axis_pitch, self.rotation_axis_yaw, self.rotation_axis_roll,
                     self.limit_pitch, self.limit_yaw, self.limit_roll,
                     self.offset_x, self.offset_y, self.offset_z,
                     self.origin_x, self.origin_y, self.origin_z)

        self.children = []


    def draw(self, draw_mode, lights, material: OpenGLMaterial = None):
        if self.limit_pitch is not None:
            if self.angle_pitch < self.limit_pitch[0]:
                self.angle_pitch = self.limit_pitch[0]
            elif self.angle_pitch > self.limit_pitch[1]:
                self.angle_pitch = self.limit_pitch[1]

        if self.limit_yaw is not None:
            if self.angle_yaw < self.limit_yaw[0]:
                self.angle_yaw = self.limit_yaw[0]
            elif self.angle_yaw > self.limit_yaw[1]:
                self.angle_yaw = self.limit_yaw[1]

        if self.limit_roll is not None:
            if self.angle_roll < self.limit_roll[0]:
                self.angle_roll = self.limit_roll[0]
            elif self.angle_roll > self.limit_roll[1]:
                self.angle_roll = self.limit_roll[1]

        # Apply rotations and draw the component
        glTranslatef(self.offset_x, self.offset_y, self.offset_z)
        glRotatef(self.angle_pitch, 1, 0, 0)  # Rotate around X-axis
        glRotatef(self.angle_yaw, 0, 1, 0)  # Rotate around Y-axis
        glRotatef(self.angle_roll, 0, 0, 1)  # Rotate around Z-axis
        glTranslatef(self.origin_x, self.origin_y, self.origin_z)



        # Draw cuboid in the specified mode
        if draw_mode == 0:
            self.cuboid.draw_point()
        elif draw_mode == 1:
            self.cuboid.draw_line()
        elif draw_mode == 2:
            self.cuboid.draw_fill()
        elif draw_mode == 3:
            self.cuboid.draw_chess()
        elif draw_mode == 4:
            self.apply_lights(lights)
            self.cuboid.draw_flat_shaded(lights, material)
        elif draw_mode == 5:
            self.apply_lights(lights)
            self.cuboid.draw_gouraud_shaded(lights, material)

        glTranslatef(-self.origin_x, -self.origin_y, -self.origin_z)

        # Draw each child component
        for child in self.children:
            glPushMatrix()
            child.draw(draw_mode, lights, material)
            glPopMatrix()