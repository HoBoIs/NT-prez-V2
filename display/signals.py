from PyQt6.QtCore import QObject, pyqtSignal
class QtBridge(QObject):
    stateUpdated = pyqtSignal(str)
