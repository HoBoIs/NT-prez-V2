from dataclasses import dataclass,field

import state.topState as topState

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
    kind="State"

    def __init__(self,ts : "topState.TopState | State"):
        self.kind="State"
        if type(ts) ==topState.TopState:
            self.topState=ts
            self.parentState=None
        elif isinstance(ts,State):
            self.topState=ts.topState
            self.parentState=ts
        self.mediaAllerts=[]
        self.childState=None
        self.imageInvert=True
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
    def getChain(self) -> list["State"]:
        res :list[State]= [self]
        if self.childState:
            res+=self.childState.getChain()
        return res
    def getAllerts(self):
        if self.childState:
            self.childState.getAllerts()
            self.mediaAllerts+=self.childState.mediaAllerts
            self.childState.mediaAllerts=[]
    def print(self):
        print(self.kind)
        if isinstance(self.childState,State) :
            self.childState.print()


    
    #text = QLabel()
    #Tformat=QtCore.Qt.TextFormat.MarkdownText
    #QtGui.QTextDocument()
    #QtGui.QTextBlock()
    #QtQuick.QQuickTextDocument()
