# gl_widget.py
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage
from OpenGL.GL import *
import math

import common

from axis import axis
from tetrahedron import tetrahedron
from cube import cube
from file_ply import read_ply, PLYObject
from object3d import object3D
from cone import cone
from cylinder import cylinder
from sphere import sphere
from hierarchial_model import HierarchicalModel, Component
from file_ply import RevolutionObject
from chess_board import ChessBoard
from texture_utils import load_texture

X_MIN = -.1
X_MAX = .1
Y_MIN = -.1
Y_MAX = .1
FRONT_PLANE_PERSPECTIVE = (X_MAX - X_MIN) / 2
BACK_PLANE_PERSPECTIVE = 1000
DEFAULT_DISTANCE = 2
ANGLE_STEP = 1
DISTANCE_FACTOR = 1.1

OBJECT_TETRAHEDRON = 0
OBJECT_CUBE = 1
OBJECT_CONE = 2
OBJECT_CYLINDER = 3
OBJECT_SPHERE = 4
OBJECT_PLY = 5
OBJECT_HIERARCHY = 6
OBJECT_CHESSBOARD = 7

FLAT_SHADING = 0
GOURAUD_SHADING = 1
TEXTURE_UNLIT = 2
TEXTURE_FLAT = 3
TEXTURE_GOURAUD = 4

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
        self.draw_fill = False
        self.draw_chess = False

        self.object = OBJECT_TETRAHEDRON
        self.ply_object = None

        self.angle_step = 1

        self.animation_active = False

        self.shading_mode = FLAT_SHADING
        self.texture_mode = TEXTURE_UNLIT

        self.light0_enabled = True
        self.light1_enabled = True
        self.material_index = 0

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
            self.draw_fill = not self.draw_fill
        elif event.key() == Qt.Key.Key_C:
            self.draw_chess = not self.draw_chess

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

        # Modify rotation speed
        if event.key() == Qt.Key.Key_E:
            self.angle_step += 0.2
            if self.angle_step > 10:
                self.angle_step = 10
        elif event.key() == Qt.Key.Key_R:
            self.angle_step -= 0.2
            if self.angle_step < 0:
                self.angle_step = 0

        # Modify rotation speed for second and third degrees of freedom
        if event.key() == Qt.Key.Key_T:
            self.arm2.angle_pitch += self.angle_step
        elif event.key() == Qt.Key.Key_Y:
            self.arm2.angle_pitch -= self.angle_step
        if event.key() == Qt.Key.Key_U:
            self.arm3.angle_pitch += self.angle_step
        elif event.key() == Qt.Key.Key_I:
            self.arm3.angle_pitch -= self.angle_step

        # Shading and texture modes
        if event.key() == Qt.Key.Key_F3:
            self.shading_mode = FLAT_SHADING
        elif event.key() == Qt.Key.Key_F4:
            self.shading_mode = GOURAUD_SHADING
        elif event.key() == Qt.Key.Key_F5:
            self.texture_mode = TEXTURE_UNLIT
        elif event.key() == Qt.Key.Key_F6:
            self.texture_mode = TEXTURE_FLAT
        elif event.key() == Qt.Key.Key_F7:
            self.texture_mode = TEXTURE_GOURAUD

        # Light control
        if event.key() == Qt.Key.Key_J:
            self.light0_enabled = not self.light0_enabled
        elif event.key() == Qt.Key.Key_K:
            self.light1_enabled = not self.light1_enabled

        # Material selection
        if event.key() == Qt.Key.Key_M:
            self.material_index = (self.material_index + 1) % 3

        # Display modes
        if event.key() == Qt.Key.Key_F1:
            self.draw_fill = True
            self.draw_chess = False
        elif event.key() == Qt.Key.Key_F2:
            self.draw_fill = False
            self.draw_chess = True

        self.update()

    def animate(self):
        if self.animation_active:
            self.arm1.angle_yaw += self.angle_step
            self.update()
        else:
            self.timer.stop()

    def start_animation(self):
        self.timer.start()

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

        if self.draw_fill:
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

        if self.draw_chess:
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

        if self.object == OBJECT_CHESSBOARD:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            self.chess_board.draw_texture()
            glDisable(GL_TEXTURE_2D)

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
        self.set_lighting()
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

    def set_lighting(self):
        glEnable(GL_LIGHTING)
        if self.light0_enabled:
            glEnable(GL_LIGHT0)
        else:
            glDisable(GL_LIGHT0)

        if self.light1_enabled:
            glEnable(GL_LIGHT1)
        else:
            glDisable(GL_LIGHT1)

        light0_position = [1.0, 1.0, 1.0, 0.0]
        light0_diffuse = [1.0, 1.0, 1.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light0_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)

        light1_position = [0.0, 1.0, 0.0, 1.0]
        light1_diffuse = [1.0, 0.0, 1.0, 1.0]
        glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)

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