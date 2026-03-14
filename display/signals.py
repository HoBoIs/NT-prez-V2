from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum
import socketio
class MEvent(Enum):
    START=1
    STOP=2
    PAUSE=3
    

class QtBridge(QObject):
    stateUpdated = pyqtSignal()
    mediaEvent   = pyqtSignal(MEvent)
    def __init__(self):
        super().__init__()
        self.sio = socketio.Client()
    def connect(self):
        
        # Connect to your Flask server
        self.sio.connect('http://localhost:8000')

    def sendUpdate(self,data={}):

        if not self.sio.connected:
            self.connect()
        if self.sio.connected:
            self.sio.emit('stateUpdated', data)

