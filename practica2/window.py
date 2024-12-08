# window.py
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QHBoxLayout, QFileDialog, QVBoxLayout, QMenu
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QAction
from gl_widget import gl_widget, PLY_PATH
import os
import random

class window(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget(self)
        self.horizontal_main = QHBoxLayout()

        self.framed_widget = QFrame(central_widget)
        self.framed_widget.setFrameStyle(QFrame.Shape.Panel)
        self.framed_widget.setLineWidth(3)

        self.gl_widget = gl_widget(self.framed_widget)
        self.horizontal_frame = QHBoxLayout()
        self.horizontal_frame.addWidget(self.gl_widget)
        self.framed_widget.setLayout(self.horizontal_frame)

        self.horizontal_main.addWidget(self.framed_widget)
        central_widget.setLayout(self.horizontal_main)

        # File menu
        action_exit = QAction('Exit', self)
        action_exit.triggered.connect(QApplication.quit)

        action_open = QAction('Open PLY file...', self)
        action_open.triggered.connect(self.open_file)

        self.menu_bar = self.menuBar()
        menu_file = self.menu_bar.addMenu('File')
        menu_file.addAction(action_open)
        menu_file.addAction(action_exit)

        # Mode menu
        self.menu_mode = self.menuBar().addMenu('Mode')
        action_single = QAction('Single', self)
        action_single.triggered.connect(self.set_single_mode)
        action_matrix = QAction('PLY Matrix', self)
        action_matrix.triggered.connect(self.set_matrix_mode)
        self.menu_mode.addAction(action_single)
        self.menu_mode.addAction(action_matrix)

        # Window settings
        self.setWindowTitle('3D Viewer')
        self.setGeometry(100, 100, 1000, 1000)
        self.setCentralWidget(central_widget)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PLY File", "", "PLY Files (*.ply)")
        if file_name:
            self.gl_widget.load_ply(file_name)

    def set_single_mode(self):
        self.gl_widget.set_mode('single')

    def set_matrix_mode(self):
        self.gl_widget.set_mode('matrix')
        self.gl_widget.load_ply_matrix(PLY_PATH)
