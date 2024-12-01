# main.py
import sys
from PySide6.QtWidgets import QApplication

from window import window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = window()
    window.show()
    sys.exit(app.exec())

    """
    Application Controls:

    P - Display in points mode
    L - Display in lines/edges mode
    F - Display in fill mode
    1 - Activate tetrahedron
    2 - Activate cube
    3 - Activate cone
    4 - Activate cylinder
    5 - Activate sphere
    6 - Activate loaded PLY object
    7 - Activate hierarchical object
    8 - Activate chessboard
    A - Activate/deactivate the animation
    Q/W - Modify first degree of freedom of the hierarchical model (increase/decrease)
    S/D - Modify second degree of freedom of the hierarchical model (increase/decrease)
    Z/X - Modify third degree of freedom of the hierarchical model (increase/decrease)
    E/R - Increase/decrease the rate of modification of the first degree of freedom of the hierarchical model
    T/Y - Increase/decrease the rate of modification of the second degree of freedom of the hierarchical model
    U/I - Increase/decrease the rate of modification of the third degree of freedom of the hierarchical model
    F1 - Solid mode display
    F2 - Display in chess mode
    F3 - Display in flat shaded lighting mode
    F4 - Gouraud shaded lighting mode display
    F5 - Display in unlit texture mode
    F6 - Display in texture mode with flat shaded lighting
    F7 - Gouraud shaded lighting texture mode display
    J - Activate/deactivate the first white light
    K - Activate/deactivate the second magenta light
    M - Consecutive selection between the three materials
    """