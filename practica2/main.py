import sys
from PySide6.QtWidgets import QApplication

from window import window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = window()
    window.show()
    sys.exit(app.exec())

    """
    Działanie aplikacji:

    P - wyświetl punkty
    L - wyświetl linie
    F - wyświetl ściany
    C - wyświetl trójkąty (chess view)
    1 - renderuj ostrosłup
    2 - renderuj sześcian
    3 - renderuj PLY
    Strzałki - obrót w 3D widoku
    +/- - zoom
    WSAD - przesuwanie w 3D widoku


    """