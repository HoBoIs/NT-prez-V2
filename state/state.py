from dataclasses import dataclass,field
import state.topState as tS

@dataclass
class State:
    def nextState(self):
        pass
    def prevState(self):
        pass
    topState : "tS.TopState"
    parentState: "None | State" =None
    childState: "None | State" =None
    imageInvert=True
    kind="State"

    def __init__(self,ts : "tS.TopState | State"):
        self.kind="State"
        if type(ts) ==tS.TopState:
            self.topState=ts
            self.parentState=None
        elif isinstance(ts,State):
            self.topState=ts.topState
            self.parentState=ts
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
    def getMedia(self)->"tS.MediaDescript | None": 
        if self.childState:
            return self.childState.getMedia()
        return None
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
    def destruct(self): 
        # destructs the state's all children. This is for avoiding memory leaks because of the circular dependencies
        if self.childState:
            self.childState.destruct()
        self.childState=None
        self.parentState=None
    def print(self):
        print(self.kind)
        if isinstance(self.childState,State) :
            self.childState.print()


    
    #text = QLabel()
    #Tformat=QtCore.Qt.TextFormat.MarkdownText
    #QtGui.QTextDocument()
    #QtGui.QTextBlock()
    #QtQuick.QQuickTextDocument()
