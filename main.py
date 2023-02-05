import sys

from PySide6 import QtWidgets, QtGui

from src.MainWidget import MainWidget


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Steam trap data analyser')
        self.setGeometry(0, 0, 800, 480)

        self._wdg_main = MainWidget()
        self.btn = QtWidgets.QPushButton('Click me')
        self.setCentralWidget(self._wdg_main)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())