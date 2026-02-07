from dataclasses import dataclass,field
from typing import TYPE_CHCKING

import server.topState as topState

@dataclass
class State:
    def nextState(self):
        pass
    def prevState(self):
        pass
    topState : "topState.TopState" 
    parentState: "None | State" =None
    childState: "None | State" =None
    imageInvert=True
    mediaAllerts:list[str]=field(default_factory=lambda:[])

    def __init__(self,ts : "topState.TopState"):
        self.topState=ts
    def notifyParentNxt(self):
        if self.parentState!=None:
            self.parentState.childEndedNxt()
    def notifyParentPrev(self):
        if self.parentState!=None:
            self.parentState.childEndedPrev()
    def childEndedNxt(self):
        pass
    def childEndedPrev(self):
        pass
    #For the phone frontend
    def nxtPrevirw(self):
        return "N/A"
    def prevPreview(self):
        return "N/A"
    def getPlayState(self):
        return (0,0)
    def getForHighlite(self):
        return "N/A"
    def getType(self):
        return "N/A"
    def getAllerts(self):
        if self.childState:
            self.childState.getAllerts()
            self.mediaAllerts+=self.childState.mediaAllerts
            self.childState.mediaAllerts=[]


    
    #text = QLabel()
    #Tformat=QtCore.Qt.TextFormat.MarkdownText
    #QtGui.QTextDocument()
    #QtGui.QTextBlock()
    #QtQuick.QQuickTextDocument()
