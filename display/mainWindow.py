from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsTextItem, QMainWindow, QVBoxLayout, QWidget, QGraphicsView
import typing
import sys
from display.signals import QtBridge
from state.song import SongState
from state.topState import TopState
from PyQt6.QtGui import QFont, QKeyEvent, QPaintDevice, QPainter, QTransform,QColor
from PyQt6.QtCore import QTimer, QUrl, Qt

class MainWindow(QMainWindow):
    state:TopState
    name:str
    scene:QGraphicsScene
    view:QGraphicsView
    textDisplay =QGraphicsTextItem()
    is_fullscreen:bool=False
    def __init__(self, s:TopState):
        super().__init__()
        self.state=s
        self.name="Display"
        self.scene=QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.scene.addItem(self.textDisplay)
        self.scene.setBackgroundBrush(QColor("white"))
        self.is_fullscreen=False

    def renderState(self,s=""):
        toR=self.state.getBonnomState()
        if type(toR)==SongState:
            self.renderVerse(toR.actual.verses[toR.verseIdx])
    def renderVerse(self,verse):
        print(verse)
        self.textDisplay.setVisible(True)
        self.textDisplay.setHtml(verse)
        pass
    def addBridge(self,b:QtBridge):
        self.bridge=b
        
        self.bridge.stateUpdated.connect(self.renderState)
    def keyPressEvent(self, a0):
        super().keyPressEvent(a0)
        if a0 and a0.key() == Qt.Key.Key_Escape:
            self.showNormal()
            self.is_fullscreen = not self.is_fullscreen

        if a0 and a0.key() == Qt.Key.Key_F11:
            if self.is_fullscreen:
                self.showNormal()
            else:
                self.showFullScreen()
            self.is_fullscreen = not self.is_fullscreen
