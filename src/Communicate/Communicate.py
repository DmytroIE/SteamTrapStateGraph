from PySide6 import QtCore

class Communicate(QtCore.QObject):
    change_status_line = QtCore.Signal(str)
    load_successful = QtCore.Signal(bool)



GlobalCommunicator = Communicate()