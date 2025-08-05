from dataclasses import dataclass
#from mainWindow import MainWindow
@dataclass
class State:
    def nextState(self):
        pass
    def prevState(self):
        pass
    mainWindow : "MainWindow"
    audioFile : None | str=None
    videoFile : None | str=None
    imageFile: None | str = None
    parentState: "None | State" =None
    childState: "None | State" =None
    imageInvert=True
    def render(self):
        pass
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


    
    #text = QLabel()
    #Tformat=QtCore.Qt.TextFormat.MarkdownText
    #QtGui.QTextDocument()
    #QtGui.QTextBlock()
    #QtQuick.QQuickTextDocument()
