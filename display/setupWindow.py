from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QCheckBox, QComboBox, QCompleter, QGridLayout, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget, QLabel
from display.signals import QtBridge
from display.songOrder import SongOrderEditor
from state.topState import TopState, dataContainer
from display.utils import DragHandle,ReorderContainer,SaveBtns,NoWheelComboBox
from display.talkEdit import TalkEdit, TalkListEdit
from state.config import Config
from PyQt6.QtCore import QSortFilterProxyModel, QStringListModel, Qt
import unicodedata
from PyQt6.QtGui import QKeySequence, QGuiApplication
import re

    



class SetupWindow(QWidget):
    layout_: QGridLayout
    state:TopState
    items:list[TalkEdit]
    tle:TalkListEdit
    soe:SongOrderEditor
    parts:list[QWidget]
    def __init__(self, s:TopState):
        super().__init__()
        self.state=s
        self.layout_=QGridLayout(self)
        self.setLayout(self.layout_)
        self.tle=TalkListEdit(self,s)
        #soe=ItemEdit(s.data,self.state.cfg)
        self.soe=SongOrderEditor(None,s.data,self.state.cfg,self.state)
        self.parts=[self.soe,self.tle]

        self.layout_.addWidget(self.tle,0,0)
        self.layout_.addWidget(self.soe,0,1)
    def addBridge(self,b:QtBridge):
        self.bridge=b
    def sendUpdate(self,data:dict={}):
        self.bridge.sendUpdate(self.state.port,data)
        #for t in s.data.talks.values():
        #    self.container.addWidget(TalkEdit(t,s.data,self.state.cfg))
            
            #self.layout_.addWidget(self.items[-1],i,0)
            #i+=1
