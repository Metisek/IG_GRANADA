from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QHBoxLayout
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QMatrix4x4, QAction

from gl_widget import gl_widget

class window(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget(self)
        horizontal_main = QHBoxLayout()

        framed_widget = QFrame(central_widget)
        framed_widget.setFrameStyle(QFrame.Shape.Panel)
        framed_widget.setLineWidth(3)

        self.gl_widget = gl_widget(framed_widget)
        horizontal_frame = QHBoxLayout()
        horizontal_frame.addWidget(self.gl_widget)
        framed_widget.setLayout(horizontal_frame)

        horizontal_main.addWidget(framed_widget)
        central_widget.setLayout(horizontal_main)

        action_exit = QAction('Exit', self)
        action_exit.triggered.connect(QApplication.quit)

        self.menu_bar = self.menuBar()
        menu_file = self.menu_bar.addMenu('File')
        menu_file.addAction(action_exit)

        # Configura la ventana
        self.setWindowTitle('Practica 1')
        self.setGeometry(100, 100, 1000, 1000)
        self.setCentralWidget(central_widget)

