# gl_widget.py
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage
from OpenGL.GL import *
import math

import common

from axis import axis
from objects.tetrahedron import tetrahedron
from objects.cube import cube
from file_ply import read_ply, PLYObject
from object3d import object3D
from objects.cone import cone
from objects.cylinder import cylinder
from objects.sphere import sphere
from objects.hierarchial_model import HierarchicalModel, Component
from file_ply import RevolutionObject
from objects.chess_board import ChessBoard
from texture_utils import load_texture
from lights import Light
from materials import OpenGLMaterial

X_MIN = -.1
X_MAX = .1
Y_MIN = -.1
Y_MAX = .1
FRONT_PLANE_PERSPECTIVE = (X_MAX - X_MIN) / 2
BACK_PLANE_PERSPECTIVE = 1000
DEFAULT_DISTANCE = 2
ANGLE_STEP = 1
HIERARCHY_ANGLE_STEP = 0.2
DISTANCE_FACTOR = 1.1

OBJECT_TETRAHEDRON = 0
OBJECT_CUBE = 1
OBJECT_CONE = 2
OBJECT_CYLINDER = 3
OBJECT_SPHERE = 4
OBJECT_PLY = 5
OBJECT_HIERARCHY = 6
OBJECT_CHESSBOARD = 7

DISPLAY_SOLID = 0
DISPLAY_CHESS = 1
DISPLAY_FLAT_SHADED = 2
DISPLAY_GOURAUD_SHADED = 3
DISPLAY_UNLIT_TEXTURE = 4
DISPLAY_TEXTURE_FLAT = 5
DISPLAY_TEXTURE_GOURAUD = 6

class gl_widget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(gl_widget, self).__init__(parent)

        self.observer_distance = DEFAULT_DISTANCE
        self.observer_angle_x = 0
        self.observer_angle_y = 0
        self.move_x = 0
        self.move_y = 0

        self.draw_point = True
        self.draw_line = False

        self.solid_enabled = False
        self.solid_mode = DISPLAY_SOLID
        self.material_index = 0

        self.object = OBJECT_TETRAHEDRON
        self.ply_object = None

        self.angle_step = 1

        self.animation_active = False

        self.setFocusPolicy(Qt.StrongFocus)

        # Code to define the QTimer for the animation
        self.timer = QTimer()
        self.timer.setInterval(0)
        self.timer.timeout.connect(self.animate)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_1:
            self.object = OBJECT_TETRAHEDRON
        elif event.key() == Qt.Key.Key_2:
            self.object = OBJECT_CUBE
        elif event.key() == Qt.Key.Key_6 and self.ply_object is not None:
            self.object = OBJECT_PLY
        elif event.key() == Qt.Key.Key_3:
            self.object = OBJECT_CONE
        elif event.key() == Qt.Key.Key_4:
            self.object = OBJECT_CYLINDER
        elif event.key() == Qt.Key.Key_5:
            self.object = OBJECT_SPHERE
        elif event.key() == Qt.Key.Key_7:
            self.object = OBJECT_HIERARCHY
        elif event.key() == Qt.Key.Key_8:
            self.object = OBJECT_CHESSBOARD

        if event.key() == Qt.Key.Key_P:
            self.draw_point = not self.draw_point
        elif event.key() == Qt.Key.Key_L:
            self.draw_line = not self.draw_line
        elif event.key() == Qt.Key.Key_F:
            self.solid_enabled = not self.solid_enabled

        if event.key() == Qt.Key.Key_Left:
            self.observer_angle_y -= ANGLE_STEP
        elif event.key() == Qt.Key.Key_Right:
            self.observer_angle_y += ANGLE_STEP
        elif event.key() == Qt.Key.Key_Up:
            self.observer_angle_x -= ANGLE_STEP
        elif event.key() == Qt.Key.Key_Down:
            self.observer_angle_x += ANGLE_STEP
        if event.key() == Qt.Key.Key_PageUp or event.key() == Qt.Key.Key_Equal:
            self.observer_distance /= DISTANCE_FACTOR
        if event.key() == Qt.Key.Key_PageDown or event.key() == Qt.Key.Key_Minus:
            self.observer_distance *= DISTANCE_FACTOR

        # Hierarchial model movement
        if event.key() == Qt.Key.Key_A:
            self.animation_active = not self.animation_active
            if self.animation_active:
                self.start_animation()
        # Base rotation
        if event.key() == Qt.Key_Q:
            self.arm1.angle_yaw += self.angle_step
        elif event.key() == Qt.Key_W:
            self.arm1.angle_yaw -= self.angle_step

        # Main arm up/down
        if event.key() == Qt.Key_S:
            self.arm2.angle_pitch += self.angle_step
        elif event.key() == Qt.Key_D:
            self.arm2.angle_pitch -= self.angle_step

        # Secondary arm up/down
        if event.key() == Qt.Key_Z:
            self.arm3.angle_pitch += self.angle_step
        elif event.key() == Qt.Key_X:
            self.arm3.angle_pitch -= self.angle_step

        # Modify rotation speed for base
        if event.key() == Qt.Key.Key_E:
            self.arm1.speed_yaw += HIERARCHY_ANGLE_STEP
            if self.arm1.speed_yaw > self.arm1.limit_speed_yaw:
                self.arm1.speed_yaw = self.arm1.limit_speed_yaw
        elif event.key() == Qt.Key.Key_R:
            self.arm1.speed_yaw -= HIERARCHY_ANGLE_STEP
            if self.arm1.speed_yaw < 0:
                self.arm1.speed_yaw = 0

        # Modify rotation speed for second and third degrees of freedom
        if event.key() == Qt.Key.Key_T:
            self.arm2.angle_pitch += HIERARCHY_ANGLE_STEP
            if self.arm2.angle_pitch > self.arm2.limit_speed_pitch:
                self.arm2.angle_pitch = self.arm2.limit_speed_pitch
        elif event.key() == Qt.Key.Key_Y:
            self.arm2.angle_pitch -= HIERARCHY_ANGLE_STEP
            if self.arm2.angle_pitch < 0:
                self.arm2.angle_pitch = 0
        if event.key() == Qt.Key.Key_U:
            self.arm3.angle_pitch += HIERARCHY_ANGLE_STEP
            if self.arm3.angle_pitch > self.arm3.limit_speed_pitch:
                self.arm3.angle_pitch = self.arm3.limit_speed_pitch
        elif event.key() == Qt.Key.Key_I:
            self.arm3.angle_pitch -= HIERARCHY_ANGLE_STEP
            if self.arm3.angle_pitch < 0:
                self.arm3.angle_pitch = 0

        # Materials
        if event.key() == Qt.Key.Key_M:
            self.material_index = (self.material_index + 1) % len(self.materials)

        # Lights
        if event.key() == Qt.Key.Key_J:
            self.enabled_lights[0] = not self.enabled_lights[0]
        elif event.key() == Qt.Key.Key_K:
            self.enabled_lights[1] = not self.enabled_lights[1]

        # Display modes
        if event.key() == Qt.Key.Key_F1:
            self.solid_mode = DISPLAY_SOLID
        elif event.key() == Qt.Key.Key_F2:
            self.solid_mode = DISPLAY_CHESS
        elif event.key() == Qt.Key.Key_F3:
            self.solid_mode = DISPLAY_FLAT_SHADED
        elif event.key() == Qt.Key.Key_F4:
            self.solid_mode = DISPLAY_GOURAUD_SHADED
        elif event.key() == Qt.Key.Key_F5:
            self.solid_mode = DISPLAY_UNLIT_TEXTURE
        elif event.key() == Qt.Key.Key_F6:
            self.solid_mode = DISPLAY_TEXTURE_FLAT
        elif event.key() == Qt.Key.Key_F7:
            self.solid_mode = DISPLAY_TEXTURE_GOURAUD

        self.update()

    def animate(self):
        if self.animation_active:
            self.arm1.angle_yaw += self.angle_step
            self.update()
            self.lights[1].position[0] = math.cos(math.radians(self.arm1.angle_yaw)) * 1.0
            self.lights[1].position[2] = math.sin(math.radians(self.arm1.angle_yaw)) * 1.0
        else:
            self.timer.stop()

    def start_animation(self):
        if not hasattr(self, 'timer'):
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.animate)
        self.timer.start(1000 // 60)

    def clear_window(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def change_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glFrustum(X_MIN, X_MAX, Y_MIN, Y_MAX, FRONT_PLANE_PERSPECTIVE, BACK_PLANE_PERSPECTIVE)

    def change_observer(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(self.move_x, self.move_y, -self.observer_distance)
        glRotatef(self.observer_angle_x, 1, 0, 0)
        glRotatef(self.observer_angle_y, 0, 1, 0)

    def draw_objects(self):
        self.axis.draw_line()

        if self.draw_point:
            glPointSize(5)
            glColor3fv(common.BLACK)
            if self.object == OBJECT_TETRAHEDRON:
                self.tetrahedron.draw_point()
            elif self.object == OBJECT_CUBE:
                self.cube.draw_point()
            elif self.object == OBJECT_PLY and self.ply_object:
                self.ply_object.draw_point()
            elif self.object == OBJECT_CONE:
                self.cone.draw_point()
            elif self.object == OBJECT_CYLINDER:
                self.cylinder.draw_point()
            elif self.object == OBJECT_SPHERE:
                self.sphere.draw_point()
            elif self.object == OBJECT_HIERARCHY:
                self.model.draw(0)
            elif self.object == OBJECT_CHESSBOARD:
                self.chess_board.draw_point()

        if self.draw_line:
            glLineWidth(3)
            glColor3fv(common.MAGENTA)
            if self.object == OBJECT_TETRAHEDRON:
                self.tetrahedron.draw_line()
            elif self.object == OBJECT_CUBE:
                self.cube.draw_line()
            elif self.object == OBJECT_PLY and self.ply_object:
                self.ply_object.draw_line()
            elif self.object == OBJECT_CONE:
                self.cone.draw_line()
            elif self.object == OBJECT_CYLINDER:
                self.cylinder.draw_line()
            elif self.object == OBJECT_SPHERE:
                self.sphere.draw_line()
            elif self.object == OBJECT_HIERARCHY:
                self.model.draw(1)
            elif self.object == OBJECT_CHESSBOARD:
                self.chess_board.draw_line()

        if self.solid_enabled:
            if self.solid_mode == DISPLAY_SOLID:
                glColor3fv(common.BLUE)
                if self.object == OBJECT_TETRAHEDRON:
                    self.tetrahedron.draw_fill()
                elif self.object == OBJECT_CUBE:
                    self.cube.draw_fill()
                elif self.object == OBJECT_PLY and self.ply_object:
                    self.ply_object.draw_fill()
                elif self.object == OBJECT_CONE:
                    self.cone.draw_fill()
                elif self.object == OBJECT_CYLINDER:
                    self.cylinder.draw_fill()
                elif self.object == OBJECT_SPHERE:
                    self.sphere.draw_fill()
                elif self.object == OBJECT_HIERARCHY:
                    self.model.draw(2)
                elif self.object == OBJECT_CHESSBOARD:
                    self.chess_board.draw_fill()

            elif self.solid_mode == DISPLAY_CHESS:
                if self.object == OBJECT_TETRAHEDRON:
                    self.tetrahedron.draw_chess()
                elif self.object == OBJECT_CUBE:
                    self.cube.draw_chess()
                elif self.object == OBJECT_PLY and self.ply_object:
                    self.ply_object.draw_chess()
                elif self.object == OBJECT_CONE:
                    self.cone.draw_chess()
                elif self.object == OBJECT_CYLINDER:
                    self.cylinder.draw_chess()
                elif self.object == OBJECT_SPHERE:
                    self.sphere.draw_chess()
                elif self.object == OBJECT_HIERARCHY:
                    self.model.draw(3)
                elif self.object == OBJECT_CHESSBOARD:
                    self.chess_board.draw_chess()

            if self.solid_mode == DISPLAY_FLAT_SHADED:
                active_lights = [light for light, enabled in zip(self.lights, self.enabled_lights) if enabled]
                material = self.materials[self.material_index]
                if self.object == OBJECT_TETRAHEDRON:
                    self.tetrahedron.draw_flat_shaded(active_lights, material)
                elif self.object == OBJECT_CUBE:
                    self.cube.draw_flat_shaded(active_lights, material)
                elif self.object == OBJECT_PLY and self.ply_object:
                    self.ply_object.draw_flat_shaded(active_lights, material)
                elif self.object == OBJECT_CONE:
                    self.cone.draw_flat_shaded(active_lights, material)
                elif self.object == OBJECT_CYLINDER:
                    self.cylinder.draw_flat_shaded(active_lights, material)
                elif self.object == OBJECT_SPHERE:
                    self.sphere.draw_flat_shaded(active_lights, material)
                elif self.object == OBJECT_HIERARCHY:
                    self.model.draw(4, active_lights)
                elif self.object == OBJECT_CHESSBOARD:
                    self.chess_board.draw_flat_shaded(active_lights)

            if self.solid_mode == DISPLAY_GOURAUD_SHADED:
                active_lights = [light for light, enabled in zip(self.lights, self.enabled_lights) if enabled]
                if self.object == OBJECT_TETRAHEDRON:
                    self.tetrahedron.draw_gouraud_shaded(active_lights)
                elif self.object == OBJECT_CUBE:
                    self.cube.draw_gouraud_shaded(active_lights)
                elif self.object == OBJECT_PLY and self.ply_object:
                    self.ply_object.draw_gouraud_shaded(active_lights)
                elif self.object == OBJECT_CONE:
                    self.cone.draw_gouraud_shaded(active_lights)
                elif self.object == OBJECT_CYLINDER:
                    self.cylinder.draw_gouraud_shaded(active_lights)
                elif self.object == OBJECT_SPHERE:
                    self.sphere.draw_gouraud_shaded(active_lights)
                elif self.object == OBJECT_HIERARCHY:
                    self.model.draw(5, active_lights)
                elif self.object == OBJECT_CHESSBOARD:
                    self.chess_board.draw_gouraud_shaded(active_lights)

        if self.animation_active:
            self.animate()

    def load_ply(self, file_name):
        self.ply_object = PLYObject(file_name)
        self.object = OBJECT_PLY
        self.update()

    def paintGL(self):
        self.clear_window()
        self.change_projection()
        self.change_observer()
        self.draw_objects()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)  # Ensure that texture mapping is enabled

        self.axis = axis()
        self.tetrahedron = tetrahedron()
        self.cube = cube()
        self.cone = cone()
        self.cylinder = cylinder()
        self.sphere = sphere()
        self.chess_board = ChessBoard()

        self.materials = [
            OpenGLMaterial("Bronze", [0.2125, 0.1275, 0.054], [0.714, 0.4284, 0.18144], [0.393548, 0.271906, 0.166721], 0.2, color=[0.8, 0.5, 0.2, 1.0]),
            OpenGLMaterial("Silver", [0.19225, 0.19225, 0.19225], [0.50754, 0.50754, 0.50754], [0.508273, 0.508273, 0.508273], 0.4, color=[0.75, 0.75, 0.75, 1.0]),
            OpenGLMaterial("Gold", [0.24725, 0.1995, 0.0745], [0.75164, 0.60648, 0.22648], [0.628281, 0.555802, 0.366065], 0.4, color=[1.0, 0.84, 0.0, 1.0])
        ]

        self.lights = [
            Light(position=[-2.0, 1.0, -10.0, 0.0],
                  ambient=[1.0, 1.0, 1.0, 1.0],
                  diffuse=[1.0, 1.0, 1.0, 1.0],
                  specular=[1.0, 1.0, 1.0, 1.0],
                  infinite=True,
                  brightness=100),
            Light(position=[1.0, 1.0, 1.0, 1.0],
                  ambient=[1.0, 0.0, 1.0, 1.0],
                  diffuse=[1.0, 0.0, 1.0, 1.0],
                  specular=[1.0, 0.0, 1.0, 1.0],
                  infinite=False,
                  brightness=0.3,
                  color=(1.0, 0.0, 1.0, 1.0))
        ]

        self.enabled_lights = [False, False]

        self.base = Component(1.0, 0.6, 0.2, 0.6, origin_y=-0.1)  # Base rotates around Z-axis
        self.arm1 = Component(1.0, 0.3, 0.3, 0.3, angle_yaw=0, rotation_axis_yaw=True, origin_y=0.15)  # Main arm rotates around Y-axis
        self.arm2 = Component(1.0, 0.25, 0.6, 0.25, angle_pitch=30, rotation_axis_pitch=True, limit_pitch=(0,80) ,origin_y=0.3, offset_y=0.3)  # Secondary arm rotates around X-axis
        self.arm3 = Component(1.0, 0.2, 0.6, 0.2, angle_pitch=30, rotation_axis_pitch=True, limit_pitch=(0,130), origin_y=0.3, offset_y=0.6)  # Tertiary arm rotates around X-axis
        self.gripper1 = Component(0.3, 0.05, 0.2, 0.05, origin_y=0.1, offset_y=0.6, offset_x=0.08)  # Gripper part 1
        self.gripper2 = Component(0.3, 0.05, 0.2, 0.05, origin_y=0.1, offset_y=0.6, offset_x=-0.08)  # Gripper part 2

        # Set up hierarchy
        self.base.children.append(self.arm1)
        self.arm1.children.append(self.arm2)
        self.arm2.children.append(self.arm3)
        self.arm3.children.append(self.gripper1)
        self.arm3.children.append(self.gripper2)
        self.model = HierarchicalModel()
        self.model.components.append(self.base)
        self.model.components.append(self.base)

        # Load texture
        self.texture_id = load_texture("chessboard_texture.png")
        glBindTexture(GL_TEXTURE_2D, self.texture_id)

    def load_texture(self, file_name):
        image = QImage(file_name)
        image = image.mirrored()
        image = image.convertToFormat(QImage.Format_RGB888)
        width = image.width()
        height = image.height()
        data = image.bits().asstring(width * height * 3)

        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)

    def load_ply_as_revolution(self, file_name):
        profile_points = self.read_ply_profile(file_name)  # Zmiana: użycie metody do wczytywania profilu
        self.object = RevolutionObject(profile_points)
        self.update()

    def read_ply_profile(self, file_name):
        """
        Odczytuje punkty profilu z pliku PLY, które będą użyte do wygenerowania obiektu rewolucji.
        Zwraca listę punktów (x, y) tworzących profil obiektu rewolucji.
        """
        vertices, _ = read_ply(file_name)
        profile_points = [(v[0], v[1]) for v in vertices if v[2] == 0]
        return profile_points
