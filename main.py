import sys

from PySide6 import QtWidgets
from PySide6.QtCore import QLocale

from src.MainWidget import MainWidget


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, **kwargs):
        QLocale.setDefault(QLocale('en'))
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Steam trap data analyser')
        self.setGeometry(0, 0, 960, 780)

        self._wdg_main = MainWidget()
        self.setCentralWidget(self._wdg_main)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())