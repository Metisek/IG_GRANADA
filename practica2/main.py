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
    Działanie aplikacji:

    P - wyświetl punkty
    L - wyświetl linie
    F - wyświetl ściany
    C - wyświetl trójkąty (chess view)
    1 - renderuj ostrosłup
    2 - renderuj sześcian
    3 - renderuj stożek
    4 - renderuj cylinder
    5 - renderuj sferę
    6 - renderuj wczytany obiekt PLY
    7 - renderuj model hierarchiczny
    A - animacja on
    Q/W - ruch 1 osi swobody
    S/D - ruch 2 osi swobody
    Z/X - ruch 3 osi swobody
    Strzałki - obrót kamery
    +/- zoom

    """