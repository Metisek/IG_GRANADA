# cuboid.py
from object3d import object3D

class Cuboid(object3D):
    def __init__(self, length, width=0.1, height=0.1, depth=1.0,
                 angle_pitch=0, angle_yaw=0, angle_roll=0,
                 rotation_axis_pitch=False, rotation_axis_yaw=False, rotation_axis_roll=False,
                 limit_pitch=None, limit_yaw=None, limit_roll=None,
                 offset_x=0, offset_y=0, offset_z=0,
                 origin_x=0, origin_y=0, origin_z=0):
        super().__init__()
        half_width = width / 2
        half_height = height / 2
        half_depth = depth / 2
        self.vertices.extend([
            (-half_width, -half_height, -half_depth),
            ( half_width, -half_height, -half_depth),
            ( half_width,  half_height, -half_depth),
            (-half_width,  half_height, -half_depth),
            (-half_width, -half_height,  half_depth),
            ( half_width, -half_height,  half_depth),
            ( half_width,  half_height,  half_depth),
            (-half_width,  half_height,  half_depth),
        ])

        # Define triangles for fill mode
        self.triangles.extend([
            (0, 1, 2), (0, 2, 3),
            (4, 5, 6), (4, 6, 7),
            (0, 1, 5), (0, 5, 4),
            (2, 3, 7), (2, 7, 6),
            (0, 3, 7), (0, 7, 4),
            (1, 2, 6), (1, 6, 5),
        ])

        self.length = length
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