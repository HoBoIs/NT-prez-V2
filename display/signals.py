from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum

class MEvent(Enum):
    START=1
    STOP=2
    PAUSE=3
    

class QtBridge(QObject):
    stateUpdated = pyqtSignal()
    mediaEvent   = pyqtSignal(MEvent)
