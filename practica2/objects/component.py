from OpenGL.GL import *
from objects.cuboid import Cuboid
from objects.sphere import Sphere
from object3d import object3D
from materials import OpenGLMaterial

class Component(object3D):
    def __init__(self,
                 angle_pitch: float = 0, angle_yaw: float = 0, angle_roll: float = 0,
                 rotation_axis_pitch: bool = False,
                 rotation_axis_yaw: bool = False,
                 rotation_axis_roll: bool = False,
                 limit_pitch: tuple[float, float] = None,
                 limit_yaw: tuple[float, float] = None,
                 limit_roll: tuple[float, float] = None,
                 limit_speed_pitch: float = 5,
                 limit_speed_yaw: float = 5,
                 limit_speed_roll: float = 5,
                 speed_pitch: float = 1, speed_yaw: float = 1, speed_roll: float = 1,
                 pos_x: float = 0, pos_y: float = 0, pos_z: float = 0,
                 move_axis_x: bool = False,
                 move_axis_y: bool = False,
                 move_axis_z: bool = False,
                 limit_move_x=None,
                 limit_move_y=None, limit_move_z=None,
                 limit_speed_move_x=0.5, limit_speed_move_y=0.5, limit_speed_move_z=0.5,
                 speed_move_x=1, speed_move_y=1, speed_move_z=1,
                 scale_x=1, scale_y=1, scale_z=1,
                 scale_axis_x=False, scale_axis_y=False, scale_axis_z=False,
                 limit_scale_x=None, limit_scale_y=None, limit_scale_z=None,
                 limit_speed_scale_x=0.5, limit_speed_scale_y=0.5, limit_speed_scale_z=0.5,
                 speed_scale_x=1, speed_scale_y=1, speed_scale_z=1,
                 offset_x=0, offset_y=0, offset_z=0,
                 origin_x=0, origin_y=0, origin_z=0,
                 object_type='CUBOID', object_properties: dict = None):

        """Acceptable types and properties:
        CUBOID: length, width, height
        SPHERE: radius, num_segments"""

        # Default component properties
        self.properties = object_properties

        # Rotation properties
        self.angle_pitch = angle_pitch
        self.angle_yaw = angle_yaw
        self.angle_roll = angle_roll
        self.rotation_axis_pitch = rotation_axis_pitch
        self.rotation_axis_yaw = rotation_axis_yaw
        self.rotation_axis_roll = rotation_axis_roll
        self.limit_pitch = limit_pitch
        self.limit_yaw = limit_yaw
        self.limit_roll = limit_roll
        self.limit_speed_pitch = limit_speed_pitch
        self.limit_speed_yaw = limit_speed_yaw
        self.limit_speed_roll = limit_speed_roll
        self.speed_pitch = speed_pitch
        self.speed_yaw = speed_yaw
        self.speed_roll = speed_roll

        # Translation (move) properties
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z
        self.move_axis_x = move_axis_x
        self.move_axis_y = move_axis_y
        self.move_axis_z = move_axis_z
        self.limit_move_x = limit_move_x
        self.limit_move_y = limit_move_y
        self.limit_move_z = limit_move_z
        self.limit_speed_move_x = limit_speed_move_x
        self.limit_speed_move_y = limit_speed_move_y
        self.limit_speed_move_z = limit_speed_move_z
        self.speed_move_x = speed_move_x
        self.speed_move_y = speed_move_y
        self.speed_move_z = speed_move_z

        # Scaling properties
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.scale_z = scale_z
        self.scale_axis_x = scale_axis_x
        self.scale_axis_y = scale_axis_y
        self.scale_axis_z = scale_axis_z
        self.limit_scale_x = limit_scale_x
        self.limit_scale_y = limit_scale_y
        self.limit_scale_z = limit_scale_z
        self.limit_speed_scale_x = limit_speed_scale_x
        self.limit_speed_scale_y = limit_speed_scale_y
        self.limit_speed_scale_z = limit_speed_scale_z
        self.speed_scale_x = speed_scale_x
        self.speed_scale_y = speed_scale_y
        self.speed_scale_z = speed_scale_z

        # Offset and origin properties for component moving
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z

        self.origin_x = origin_x
        self.origin_y = origin_y
        self.origin_z = origin_z

        # Object type and properties (creating cuboid as default)
        if object_type == 'CUBOID':
            if object_properties is not None:
                length = object_properties.get('length', None)
                width = object_properties.get('width', None)
                height = object_properties.get('height', None)
                self.object = Cuboid(length=length, width=width, height=height)
        elif object_type == 'SPHERE':
            radius = object_properties.get('radius', None)
            num_segments = object_properties.get('num_segments', None)
            self.object = Sphere(radius=radius, num_segments=num_segments)
        else:
            self.object = Cuboid()


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

        if self.limit_move_x is not None:
            if self.pos_x < self.limit_move_x[0]:
                self.pos_x = self.limit_move_x[0]
            elif self.pos_x > self.limit_move_x[1]:
                self.pos_x = self.limit_move_x[1]

        if self.limit_move_y is not None:
            if self.pos_y < self.limit_move_y[0]:
                self.pos_y = self.limit_move_y[0]
            elif self.pos_y > self.limit_move_y[1]:
                self.pos_y = self.limit_move_y[1]

        if self.limit_move_z is not None:
            if self.pos_z < self.limit_move_z[0]:
                self.pos_z = self.limit_move_z[0]
            elif self.pos_z > self.limit_move_z[1]:
                self.pos_z = self.limit_move_z[1]

        if self.limit_scale_x is not None:
            if self.scale_x < self.limit_scale_x[0]:
                self.scale_x = self.limit_scale_x[0]
            elif self.scale_x > self.limit_scale_x[1]:
                self.scale_x = self.limit_scale_x[1]

        if self.limit_scale_y is not None:
            if self.scale_y < self.limit_scale_y[0]:
                self.scale_y = self.limit_scale_y[0]
            elif self.scale_y > self.limit_scale_y[1]:
                self.scale_y = self.limit_scale_y[1]

        if self.limit_scale_z is not None:
            if self.scale_z < self.limit_scale_z[0]:
                self.scale_z = self.limit_scale_z[0]
            elif self.scale_z > self.limit_scale_z[1]:
                self.scale_z = self.limit_scale_z[1]

        # Apply translations, scaling, and rotations
        glTranslatef(self.pos_x, self.pos_y, self.pos_z)
        glScalef(self.scale_x, self.scale_y, self.scale_z)
        glTranslatef(self.offset_x, self.offset_y, self.offset_z)
        glRotatef(self.angle_pitch, 1, 0, 0)  # Rotate around X-axis
        glRotatef(self.angle_yaw, 0, 1, 0)  # Rotate around Y-axis
        glRotatef(self.angle_roll, 0, 0, 1)  # Rotate around Z-axis
        glTranslatef(self.origin_x, self.origin_y, self.origin_z)


        if draw_mode == 0:
            self.object.draw_point()
        elif draw_mode == 1:
            self.object.draw_line()
        elif draw_mode == 2:
            self.object.draw_fill()
        elif draw_mode == 3:
            self.object.draw_chess()
        elif draw_mode == 4:
            self.object.draw_flat_shaded(lights=lights, material = material, apply_lights=True)
        elif draw_mode == 5:
            self.object.draw_gouraud_shaded(lights=lights, material = material, apply_lights=True)

        glTranslatef(-self.origin_x, -self.origin_y, -self.origin_z)

        # Draw each child component
        for child in self.children:
            glPushMatrix()
            child.draw(draw_mode, lights, material)
            glPopMatrix()