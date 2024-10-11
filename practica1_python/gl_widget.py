from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt
from OpenGL.GL import *

import common

from axis import axis
from tetrahedron import tetrahedron
from cube import cube

X_MIN = -.1
X_MAX = .1
Y_MIN = -.1
Y_MAX = .1
FRONT_PLANE_PERSPECTIVE = (X_MAX-X_MIN)/2
BACK_PLANE_PERSPECTIVE = 1000
DEFAULT_DISTANCE = 2
ANGLE_STEP = 1
DISTANCE_FACTOR = 1.1

OBJECT_TETRAHEDRON = 0
OBJECT_CUBE = 1

class gl_widget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(gl_widget, self).__init__(parent)

        self.observer_distance = DEFAULT_DISTANCE
        self.observer_angle_x = 0
        self.observer_angle_y = 0

        self.draw_point = True
        self.draw_line = False
        self.draw_fill = False
        self.draw_chess = False

        self.object = OBJECT_TETRAHEDRON

        # importante para capturar los eventos
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_1:
            self.object = OBJECT_TETRAHEDRON
        elif event.key() == Qt.Key.Key_2:
            self.object = OBJECT_CUBE

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
        if event.key() == Qt.Key.Key_PageUp:
            self.observer_distance *= DISTANCE_FACTOR
        if event.key() == Qt.Key.Key_PageDown:
            self.observer_distance /= DISTANCE_FACTOR

        self.update()

    def clear_window(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def change_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # formato(x_minimo, x_maximo, y_minimo, y_maximo, Front_plane, plano_traser)
        # Front_plane > 0  Back_plane > PlanoDelantero)
        glFrustum(X_MIN, X_MAX, Y_MIN, Y_MAX, FRONT_PLANE_PERSPECTIVE, BACK_PLANE_PERSPECTIVE)

    def change_observer(self):
        # posicion del observador
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -self.observer_distance)
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

        if self.draw_line:
            glLineWidth(3)
            glColor3fv(common.MAGENTA)
            if self.object == OBJECT_TETRAHEDRON:
                self.tetrahedron.draw_line()
            elif self.object == OBJECT_CUBE:
                self.cube.draw_line()

        if self.draw_fill:
            glColor3fv(common.BLUE)
            if self.object == OBJECT_TETRAHEDRON:
                self.tetrahedron.draw_fill()
            elif self.object == OBJECT_CUBE:
                self.cube.draw_fill()

        if self.draw_chess:
            if self.object == OBJECT_TETRAHEDRON:
                self.tetrahedron.draw_chess()
            elif self.object == OBJECT_CUBE:
                self.cube.draw_chess()


    def paintGL(self):
        self.clear_window()
        self.change_projection()
        self.change_observer()
        self.draw_objects()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def initializeGL(self):
        # Configura el color de fondo
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_DEPTH_TEST)


        self.axis = axis()
        self.tetrahedron = tetrahedron()
        self.cube = cube()
