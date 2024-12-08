# gl_widget.py
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage
from OpenGL.GL import *
import math

import common
from OpenGL.GLU import gluNewQuadric, gluSphere

from axis import axis
from objects.tetrahedron import tetrahedron
from objects.cube import cube
from file_ply import read_ply, PLYObject
from object3d import object3D
from objects.cone import cone
from objects.cylinder import cylinder
from objects.sphere import Sphere
from objects.hierarchial_model import HierarchicalModel
from objects.component import Component
from file_ply import RevolutionObject
from objects.chess_board import ChessBoard
from texture_utils import load_texture
from lights import Light
from materials import OpenGLMaterial
import numpy as np

from OpenGL.GLU import gluUnProject
from PySide6.QtGui import QPainter

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
        self.move_z = 0
        self.last_mouse_position = None
        self.selected_triangle = None
        self.color = (255, 255, 255)

        self.draw_point = True
        self.draw_line = False

        self.solid_enabled = False
        self.solid_mode = DISPLAY_SOLID
        self.material_index = 0

        self.object = OBJECT_TETRAHEDRON
        self.ply_object = None

        self.angle_step = 1
        self.light_angle = 0

        self.animation_active = False
        self.projection_mode = 'perspective'

        self.setFocusPolicy(Qt.StrongFocus)

        # Code to define the QTimer for the animation
        self.timer = QTimer()
        self.timer.setInterval(0)
        self.timer.timeout.connect(self.animate)

    def mousePressEvent(self, event):
        self.last_mouse_position = event.pos()
        if event.button() == Qt.LeftButton:
            x, y = event.x(), event.y()
            self.makeCurrent()
            selected_index =  self.pick(x, y)
            selected_object = self.get_object_selection()
            if selected_index != -1:
                selected_object.selected_triangle = selected_index
            else:
                selected_object.selected_triangle = None
            self.update()
        elif event.button() == Qt.MiddleButton:
            self.setCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setCursor(Qt.ArrowCursor)

    def mouseMoveEvent(self, event):
        if self.last_mouse_position is not None:
            dx = event.x() - self.last_mouse_position.x()
            dy = event.y() - self.last_mouse_position.y()
            if event.buttons() & Qt.RightButton:
                self.observer_angle_x = (self.observer_angle_x + dy * ANGLE_STEP)
                if self.observer_angle_x < -90:
                    self.observer_angle_x = -90
                elif self.observer_angle_x > 90:
                    self.observer_angle_x = 90
                self.observer_angle_y = (self.observer_angle_y + dx * ANGLE_STEP) % 360
            elif event.buttons() & Qt.MiddleButton:
                move_vector = np.array([dx * 0.01, -dy * 0.01, 0.0])
                transformed_vector = self.transform_vector_by_rotation(move_vector)
                self.move_x += transformed_vector[0]
                self.move_y += transformed_vector[1]
                self.move_z += transformed_vector[2]
            self.update()
        self.last_mouse_position = event.pos()


    def transform_vector_by_rotation(self, vector):
        rotation_matrix = self.create_rotation_matrix(self.observer_angle_x, self.observer_angle_y)
        return np.dot(rotation_matrix, vector)

    def create_rotation_matrix(self, angle_x, angle_y, angle_z=0):
        angle_x, angle_y, angle_z = map(math.radians, [angle_x, angle_y, angle_z])
        rx = np.array([
            [1, 0, 0],
            [0, math.cos(angle_x), -math.sin(angle_x)],
            [0, math.sin(angle_x), math.cos(angle_x)]
        ])
        ry = np.array([
            [math.cos(angle_y), 0, math.sin(angle_y)],
            [0, 1, 0],
            [-math.sin(angle_y), 0, math.cos(angle_y)]
        ])
        rz = np.array([
            [math.cos(angle_z), -math.sin(angle_z), 0],
            [math.sin(angle_z), math.cos(angle_z), 0],
            [0, 0, 1]
        ])
        return np.dot(rz, np.dot(ry, rx))

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120  # Each step is 15 degrees
        self.observer_distance *= (1.0 - delta * 0.1)
        self.update()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_C:
            self.projection_mode = 'perspective'
        elif event.key() == Qt.Key.Key_V:
            self.projection_mode = 'parallel'

        if self.solid_mode not in {DISPLAY_UNLIT_TEXTURE, DISPLAY_TEXTURE_FLAT, DISPLAY_TEXTURE_GOURAUD}:
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

        # Hierarchial model and light movement
        if event.key() == Qt.Key.Key_A:
            self.animation_active = not self.animation_active
            if self.animation_active:
                self.start_animation()

        # Hierarchial model movement as a method
        self.move_hierarchial_model(event)

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
        aspect_ratio = self.width() / self.height()
        if self.projection_mode == 'perspective':
            glFrustum(X_MIN, X_MAX, Y_MIN, Y_MAX, FRONT_PLANE_PERSPECTIVE, BACK_PLANE_PERSPECTIVE)
        elif self.projection_mode == 'parallel':
            glOrtho(X_MIN * self.observer_distance, X_MAX * self.observer_distance,
                    Y_MIN * self.observer_distance, Y_MAX * self.observer_distance,
                    FRONT_PLANE_PERSPECTIVE, BACK_PLANE_PERSPECTIVE)

    def change_observer(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -self.observer_distance)
        glRotatef(self.observer_angle_x, 1, 0, 0)
        glRotatef(self.observer_angle_y, 0, 1, 0)
        glTranslatef(self.move_x, self.move_y, -self.move_z)
        self.update_lights()

    def update_lights(self):
        flat_modes = {DISPLAY_FLAT_SHADED, DISPLAY_TEXTURE_FLAT}
        smooth_modes = {DISPLAY_GOURAUD_SHADED, DISPLAY_TEXTURE_GOURAUD}

        for i, light in enumerate(self.lights):
            if self.enabled_lights[i]:
                glEnable(GL_LIGHT0 + i)
                position = np.array(light.position + [0.0 if light.infinite else 1.0], dtype=np.float32)
                glLightfv(GL_LIGHT0 + i, GL_POSITION, position)
                glLightfv(GL_LIGHT0 + i, GL_AMBIENT, light.ambient)
                glLightfv(GL_LIGHT0 + i, GL_DIFFUSE, [c * light.brightness for c in light.diffuse])
                glLightfv(GL_LIGHT0 + i, GL_SPECULAR, [c * light.brightness for c in light.specular])
                # Draw light as a circle in space
                color = light.color
                if color == (1.0, 1.0, 1.0, 1.0):
                    color = (0.0, 0.0, 0.0, 1.0)
                glMaterialfv(GL_FRONT, GL_EMISSION, color)
                glPushMatrix()
                glTranslatef(*light.position)
                quadric = gluNewQuadric()
                gluSphere(quadric, 0.05, 16, 16)  # Small sphere with radius 0.05
                glPopMatrix()
                glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])

                if self.solid_mode in flat_modes:
                    glShadeModel(GL_FLAT)
                elif self.solid_mode in smooth_modes:
                    glShadeModel(GL_SMOOTH)
            else:
                glDisable(GL_LIGHT0 + i)

    def get_object_selection(self):
        if self.object == OBJECT_TETRAHEDRON:
            return self.tetrahedron
        elif self.object == OBJECT_CUBE:
            return self.cube
        elif self.object == OBJECT_PLY:
            return self.ply_object
        elif self.object == OBJECT_CONE:
            return self.cone
        elif self.object == OBJECT_CYLINDER:
            return self.cylinder
        elif self.object == OBJECT_SPHERE:
            return self.sphere
        elif self.object == OBJECT_HIERARCHY:
            return self.model
        elif self.object == OBJECT_CHESSBOARD:
            return self.chess_board

    def draw_objects(self):
        self.axis.draw_line()
        self.selected_object = self.get_object_selection()
        material = self.materials[self.material_index]

        if self.solid_enabled:
            if self.solid_mode == DISPLAY_SOLID:
                glColor3fv(common.BLUE)
                if self.object != OBJECT_HIERARCHY:
                    self.selected_object.draw_fill()
                else:
                    self.model.draw(2)

            elif self.solid_mode == DISPLAY_CHESS:
                if self.object != OBJECT_HIERARCHY:
                    self.selected_object.draw_chess()
                else:
                    self.model.draw(3)

            if self.solid_mode == DISPLAY_FLAT_SHADED:
                glEnable(GL_LIGHTING)
                if self.object != OBJECT_HIERARCHY:
                    self.selected_object.draw_flat_shaded(material)
                else:
                    self.model.draw(4, material)

            if self.solid_mode == DISPLAY_GOURAUD_SHADED:
                glEnable(GL_LIGHTING)
                if self.object != OBJECT_HIERARCHY:
                    self.selected_object.draw_gouraud_shaded(material)
                else:
                    self.model.draw(5, material)

            if self.solid_mode == DISPLAY_UNLIT_TEXTURE:
                check = self.texture_object_check()
                self.selected_object.draw_unlit_texture(self.clear_white_material)
                if check:
                    self.update()

            if self.solid_mode == DISPLAY_TEXTURE_FLAT:
                glEnable(GL_LIGHTING)
                check = self.texture_object_check()
                self.selected_object.draw_texture_flat_shaded(self.clear_white_material)
                if check:
                    self.update()

            if self.solid_mode == DISPLAY_TEXTURE_GOURAUD:
                glEnable(GL_LIGHTING)
                check = self.texture_object_check()
                self.selected_object.draw_texture_gouraud_shaded(self.clear_white_material)
                if check:
                    self.update()

        glDisable(GL_LIGHTING)
        if self.draw_point:
            glPointSize(5)
            glColor3fv(common.BLACK)
            if self.object != OBJECT_HIERARCHY:
                self.selected_object.draw_point()
            else:
                self.model.draw(0)

        if self.draw_line:
            glLineWidth(3)
            glColor3fv(common.MAGENTA)
            if self.object != OBJECT_HIERARCHY:
                self.selected_object.draw_line()
            else:
                self.model.draw(1)

        if self.animation_active:
            self.animate()

    def draw_selection(self):
        glBegin(GL_TRIANGLES)
        for i, triangle in enumerate(self.selected_object.triangles):
            color = self.int_to_color(i)
            glColor3fv(color)
            for vertex_index in triangle:
                glVertex3fv(self.selected_object.vertices[vertex_index])
        glEnd()

    def texture_object_check(self):
        if self.object != OBJECT_CHESSBOARD:
            self.object = OBJECT_CHESSBOARD
            print("Forcing object with texture...")
            self.selected_object = self.chess_board
            return True
        return False

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
        self.sphere = Sphere(1, 12)
        self.init_hierarchial_model()
        self.chess_board = ChessBoard()

        self.materials = [
            OpenGLMaterial(
                name="Gold",
                ambient=[0.24725, 0.1995, 0.0745, 1.0],
                diffuse=[0.75164, 0.60648, 0.22648, 1.0],
                specular=[0.628281, 0.555802, 0.366065, 1.0],
                shininess=35,
                color=[1.0, 0.84, 0.0, 1.0],  # Złoty odcień
            ),
            OpenGLMaterial(
                name="Red Plastic",
                ambient=[0.0, 0.0, 0.0, 1.0],
                diffuse=[0.5, 0.0, 0.0, 1.0],
                specular=[0.7, 0.6, 0.6, 1.0],
                shininess=40,
                color=[1.0, 0.0, 0.0, 1.0],  # Czerwony odcień
            ),
            OpenGLMaterial(
                name="Emerald",
                ambient=[0.0215, 0.1745, 0.0215, 1.0],
                diffuse=[0.07568, 0.61424, 0.07568, 1.0],
                specular=[0.633, 0.727811, 0.633, 1.0],
                shininess=20,
                color=[0.1, 0.8, 0.1, 1.0],  # Zielony odcień
            ),
        ]

        self.clear_white_material = OpenGLMaterial(
            name="White",
            ambient=[0.0, 0.0, 0.0, 1.0],
            diffuse=[1.0, 1.0, 1.0, 1.0],
            specular=[1.0, 1.0, 1.0, 1.0],
            shininess=50,
            color=[1.0, 1.0, 1.0, 1.0]
        )


        self.lights = [
            Light(position=[-2.0, 1.0, -10.0],
                ambient=[1.0, 1.0, 1.0, 1.0],
                diffuse=[1.0, 1.0, 1.0, 1.0],
                specular=[1.0, 1.0, 1.0, 1.0],
                infinite=True,
                brightness=1),
            Light(position=[0.0, 1.0, 3.0],
                ambient=[1.0, 1.0, 1.0, 1.0],
                diffuse=[1.0, 0.0, 1.0, 1.0],
                specular=[1.0, 0.0, 1.0, 1.0],
                color=[1.0, 0.0, 1.0, 1.0],
                infinite=False,
                brightness=1)
        ]

        self.enabled_lights = [True, False]

        # Load texture
        self.texture_id = load_texture("chessboard_texture.png")
        self.chess_board.texture_id = self.texture_id

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

   # gl_widget.py
    def pick(self, x, y):
        self.makeCurrent()
        # Frame Buffer Object to do the off-screen rendering
        FBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, FBO)

        # Texture for drawing
        color_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, color_texture)
        # RGBA8
        glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, self.width(), self.height())
        # This implies that there is no mip mapping
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        # Texture for computing the depth
        depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, depth_texture)
        glTexStorage2D(GL_TEXTURE_2D, 1, GL_DEPTH_COMPONENT24, self.width(), self.height())

        # Attachment of textures to the FBO
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, color_texture, 0)
        glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, depth_texture, 0)

        # OpenGL will draw to these buffers (only one in this case)
        draw_buffers = [GL_COLOR_ATTACHMENT0]
        glDrawBuffers(1, draw_buffers)

        # Draw the scene for selection
        self.clear_window()
        self.change_projection()
        self.change_observer()
        selected_object = self.get_object_selection()
        selected_object.draw_with_ids()

        # Get the pixel color
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        color = glReadPixels(x, self.height() - y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE)

        # Convert from RGB to identifier
        r, g, b, a = color[0], color[1], color[2], color[3]
        identifier = (r << 16) | (g << 8) | b

        # Update the identifier of the selected part in the object
        selected_object.selected_triangle = identifier

        glDeleteTextures(1, [color_texture])
        glDeleteTextures(1, [depth_texture])
        glDeleteFramebuffers(1, [FBO])
        # The normal framebuffer takes control of drawing
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.defaultFramebufferObject())

        return identifier


    # New hierarchial model (simple helicopter with an arm below)
    def init_hierarchial_model(self):
        self.base = Component(object_properties={
            "file_name": "helicopter_ply/base.ply",
        }, object_type='PLY', origin_y=0.1, origin_x=0.7, origin_z=-1.3,
            pos_x=0, move_axis_x=True, limit_move_x=(-5, 5),
            speed_move_x=0.1, limit_speed_move_x=0.5)

        self.main_rotor = Component(object_properties={
            "file_name": "helicopter_ply/rotor_big.ply",
            }, object_type='PLY', origin_y=-0.4, offset_y=3.15, offset_x=-0.84,
           rotation_axis_yaw=True, angle_yaw=0)

        self.side_motor = Component(object_properties={
            "file_name": "helicopter_ply/rotor_small.ply",
            }, object_type='PLY', offset_y=1.73, offset_x=-3.5, offset_z=-0.7,
            rotation_axis_roll=True, angle_roll=0)

        self.arm_base = Component(object_properties={
            "length":0.3,
            "width":0.8,
            "height":0.3,
            }, object_type='CUBOID', origin_y=-0.4,
            offset_y=0.66, offset_x=-0.7, offset_z=-0.03)

        self.arm_extendable = Component(object_properties={
            "length":0.25,
            "width":0.8,
            "height":0.25,
            }, object_type='CUBOID', origin_y=-0.4, offset_y=0, pos_y=-0.8,
            scale_axis_y=True, limit_scale_y=(0.3, 3), speed_scale_y=0.1, scale_y=1,
            rotation_axis_yaw=True, angle_yaw=0)

        self.arm_end_gripper_1 = Component(object_properties={
            "length":0.05,
            "width":0.2,
            "height":0.05,
        }, object_type='CUBOID', origin_y=0.1, offset_y=-1, offset_x=0.08)

        self.arm_end_gripper_2 = Component(object_properties={
            "length":0.05,
            "width":0.2,
            "height":0.05,
        }, object_type='CUBOID', origin_y=0.1, offset_y=-1, offset_x=-0.08)

        self.base.children.append(self.main_rotor)
        self.base.children.append(self.side_motor)
        self.base.children.append(self.arm_base)
        self.arm_base.children.append(self.arm_extendable)
        self.arm_extendable.children.append(self.arm_end_gripper_1)
        self.arm_extendable.children.append(self.arm_end_gripper_2)
        self.model = HierarchicalModel()
        self.model.components.append(self.base)

    def animate(self):
        if self.animation_active:
            self.main_rotor.angle_yaw += self.angle_step * 12
            self.side_motor.angle_roll += self.angle_step * 8
            self.update()
            self.light_angle = (self.light_angle + self.angle_step) % 360
            self.lights[1].position[0] = math.cos(math.radians(self.light_angle)) * 2.5
            self.lights[1].position[2] = math.sin(math.radians(self.light_angle)) * 2.5
        else:
            self.timer.stop()

    def move_hierarchial_model(self, event):
        # Base x movement
        if event.key() == Qt.Key_Q:
            self.base.pos_x += self.base.speed_move_x
        elif event.key() == Qt.Key_W:
            self.base.pos_x -= self.base.speed_move_x

        # Helicopter arm scaling
        if event.key() == Qt.Key_S:
            self.arm_extendable.scale_y += self.arm_extendable.speed_scale_y
        elif event.key() == Qt.Key_D:
            self.arm_extendable.scale_y -= self.arm_extendable.speed_scale_y

        # Helicopter arm rotation
        if event.key() == Qt.Key_Z:
            self.arm_extendable.angle_yaw += self.arm_extendable.speed_yaw
        elif event.key() == Qt.Key_X:
            self.arm_extendable.angle_yaw -= self.arm_extendable.speed_yaw

        # # Modify rotation speed for base
        # if event.key() == Qt.Key.Key_E:
        #     self.arm1.speed_yaw += HIERARCHY_ANGLE_STEP
        #     if self.arm1.speed_yaw > self.arm1.limit_speed_yaw:
        #         self.arm1.speed_yaw = self.arm1.limit_speed_yaw
        # elif event.key() == Qt.Key.Key_R:
        #     self.arm1.speed_yaw -= HIERARCHY_ANGLE_STEP
        #     if self.arm1.speed_yaw < 0:
        #         self.arm1.speed_yaw = 0

        # # Modify rotation speed for second and third degrees of freedom
        # if event.key() == Qt.Key.Key_T:
        #     self.arm2.angle_pitch += HIERARCHY_ANGLE_STEP
        #     if self.arm2.angle_pitch > self.arm2.limit_speed_pitch:
        #         self.arm2.angle_pitch = self.arm2.limit_speed_pitch
        # elif event.key() == Qt.Key.Key_Y:
        #     self.arm2.angle_pitch -= HIERARCHY_ANGLE_STEP
        #     if self.arm2.angle_pitch < 0:
        #         self.arm2.angle_pitch = 0
        # if event.key() == Qt.Key.Key_U:
        #     self.arm3.angle_pitch += HIERARCHY_ANGLE_STEP
        #     if self.arm3.angle_pitch > self.arm3.limit_speed_pitch:
        #         self.arm3.angle_pitch = self.arm3.limit_speed_pitch
        # elif event.key() == Qt.Key.Key_I:
        #     self.arm3.angle_pitch -= HIERARCHY_ANGLE_STEP
        #     if self.arm3.angle_pitch < 0:
        #         self.arm3.angle_pitch = 0

    # Old hierarchial model (robot arm)
    # def init_hierarchial_model(self):
    #     self.base = Component(object_properties={
    #         "length":0.6,
    #         "width":0.2,
    #         "height":0.6,
    #     }, object_type='CUBOID', origin_y=-0.1)  # Base rotates around Z-axis

    #     self.arm1 = Component(object_properties={
    #         "length":0.3,
    #         "width":0.3,
    #         "height":0.3,
    #         }, object_type="CUBOID",
    #         angle_yaw=0, rotation_axis_yaw=True, origin_y=0.15)  # Main arm rotates around Y-axis

    #     self.arm2 = Component(object_properties={
    #         "length":0.25,
    #         "width":0.6,
    #         "height":0.25
    #         }, object_type='CUBOID',
    #         angle_pitch=30, rotation_axis_pitch=True,
    #         limit_pitch=(0,80), origin_y=0.3, offset_y=0.3)  # Secondary arm rotates around X-axis

    #     self.arm3 = Component(object_properties={
    #         "length":0.2,
    #         "width":0.6,
    #         "height":0.2
    #         }, object_type='CUBOID',
    #         angle_pitch=30, rotation_axis_pitch=True,
    #         limit_pitch=(0,130), origin_y=0.3, offset_y=0.6)  # Tertiary arm rotates around X-axis
    #     self.gripper1 = Component(object_properties={
    #         "length":0.05,
    #         "width":0.2,
    #         "height":0.05
    #         }, object_type='CUBOID',
    #         origin_y=0.1, offset_y=0.6, offset_x=0.08)  # Gripper part 1
    #     self.gripper2 = Component(object_properties={
    #         "length":0.05,
    #         "width":0.2,
    #         "height":0.05
    #         }, object_type='CUBOID',
    #         origin_y=0.1, offset_y=0.6, offset_x=-0.08)  # Gripper part 2

    #     # Set up hierarchy
    #     self.base.children.append(self.arm1)
    #     self.arm1.children.append(self.arm2)
    #     self.arm2.children.append(self.arm3)
    #     self.arm3.children.append(self.gripper1)
    #     self.arm3.children.append(self.gripper2)
    #     self.model = HierarchicalModel()
    #     self.model.components.append(self.base)

    # def move_hierarchial_model(self, event):
    #     # Base rotation
    #     if event.key() == Qt.Key_Q:
    #         self.arm1.angle_yaw += self.angle_step
    #     elif event.key() == Qt.Key_W:
    #         self.arm1.angle_yaw -= self.angle_step

    #     # Main arm up/down
    #     if event.key() == Qt.Key_S:
    #         self.arm2.angle_pitch += self.angle_step
    #     elif event.key() == Qt.Key_D:
    #         self.arm2.angle_pitch -= self.angle_step

    #     # Secondary arm up/down
    #     if event.key() == Qt.Key_Z:
    #         self.arm3.angle_pitch += self.angle_step
    #     elif event.key() == Qt.Key_X:
    #         self.arm3.angle_pitch -= self.angle_step

    #     # Modify rotation speed for base
    #     if event.key() == Qt.Key.Key_E:
    #         self.arm1.speed_yaw += HIERARCHY_ANGLE_STEP
    #         if self.arm1.speed_yaw > self.arm1.limit_speed_yaw:
    #             self.arm1.speed_yaw = self.arm1.limit_speed_yaw
    #     elif event.key() == Qt.Key.Key_R:
    #         self.arm1.speed_yaw -= HIERARCHY_ANGLE_STEP
    #         if self.arm1.speed_yaw < 0:
    #             self.arm1.speed_yaw = 0

    #     # Modify rotation speed for second and third degrees of freedom
    #     if event.key() == Qt.Key.Key_T:
    #         self.arm2.angle_pitch += HIERARCHY_ANGLE_STEP
    #         if self.arm2.angle_pitch > self.arm2.limit_speed_pitch:
    #             self.arm2.angle_pitch = self.arm2.limit_speed_pitch
    #     elif event.key() == Qt.Key.Key_Y:
    #         self.arm2.angle_pitch -= HIERARCHY_ANGLE_STEP
    #         if self.arm2.angle_pitch < 0:
    #             self.arm2.angle_pitch = 0
    #     if event.key() == Qt.Key.Key_U:
    #         self.arm3.angle_pitch += HIERARCHY_ANGLE_STEP
    #         if self.arm3.angle_pitch > self.arm3.limit_speed_pitch:
    #             self.arm3.angle_pitch = self.arm3.limit_speed_pitch
    #     elif event.key() == Qt.Key.Key_I:
    #         self.arm3.angle_pitch -= HIERARCHY_ANGLE_STEP
    #         if self.arm3.angle_pitch < 0:
    #             self.arm3.angle_pitch = 0

    # def animate(self):
    #     if self.animation_active:
    #         self.arm1.angle_yaw += self.angle_step
    #         self.update()
    #         self.light_angle = (self.light_angle + self.angle_step) % 360
    #         self.lights[1].position[0] = math.cos(math.radians(self.light_angle)) * 2.0
    #         self.lights[1].position[2] = math.sin(math.radians(self.light_angle)) * 2.0
    #     else:
    #         self.timer.stop()