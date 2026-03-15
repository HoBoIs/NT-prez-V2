from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum
from PyQt6.QtWidgets import QMessageBox
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
    def connect(self,port:int):
        
        # Connect to your Flask server
        try:
            self.sio.connect('http://localhost:'+str(port))

        except:
            QMessageBox.information(None,"Connnection failed","A kapcsolat sikertelen\nPróbáld meg telepíteni:\npip install requests\npip install websocket-client")
            "pip install requests"
            "pip install websocket-client"


    def sendUpdate(self,port:int,data={}):

        if not self.sio.connected:
            self.connect(port)
        if self.sio.connected:
            self.sio.emit('stateUpdated', data)

