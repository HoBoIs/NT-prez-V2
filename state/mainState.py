from dataclasses import dataclass
from threading import Lock
from server.topState import TopState

"""
class StateMgr:
    def __init__ (self):
        self._state = TopState()
        self._lock=Lock()
        self._listeners=[]
        self._commandListeners=[]
    def getState(self):
        with self._lock:
            return self._state
    def subscribe(self, callback):
        self._listeners.append(callback)
    def subscribeMedia(self, callback):
        self._commandListeners.append(callback)
    def _notify(self):
        for cb in self._listeners:
            cb(self.getState())
    def _mediaCommand(self,cmd):
        for cb in self._commandListeners:
            cb(cmd)
            """
