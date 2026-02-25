from PyQt6.QtWidgets import QApplication, QBoxLayout, QGraphicsScene, QGraphicsTextItem, QLabel, QMainWindow, QVBoxLayout, QWidget, QGraphicsView,QVBoxLayout
from PyQt6.QtCore import Qt
import typing
import sys
from display.signals import QtBridge
from state.imageState import Image, ImageState
from state.song import SongState
from state.titleState import Title, TitleState
from state.topState import TopState
from PyQt6.QtGui import QFont, QKeyEvent, QPaintDevice, QPainter, QPixmap, QTransform,QColor
from PyQt6.QtCore import QTimer, QUrl, Qt
from PyQt6.QtGui import QFontMetrics,QTextDocument

def html_bounding_rect(html: str, font: QFont):
    doc = QTextDocument()
    doc.setDefaultFont(font)
    doc.setHtml(html)
    #doc.setTextWidth(max_width)   # force wrapping to label width
    return doc.size()

class MainWindow(QWidget):
    state:TopState
    name:str
    layout_:QVBoxLayout
    scene:QGraphicsScene
    view:QGraphicsView
    background:QWidget
    textDisplay :QLabel
    is_fullscreen:bool=False
    def __init__(self, s:TopState):
        super().__init__()
        self.layout_ = QVBoxLayout()
        self.state=s
        self.name="Display"
        self.setStyleSheet("background-color: black;")
        self.setLayout(self.layout_)
        self.adjustBorders()
        self.textDisplay =QLabel()
        self.textDisplay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resize(800, 600)
        self.setMinimumSize(200,100)

    def renderState(self,s=""):
        toR=self.state.getBonnomState()
        self.clearLayout()
        if type(toR)==SongState:
            self.renderVerse(toR.actual.verses[toR.verseIdx])
        elif type(toR)==ImageState:
            self.renderImage(toR.image)
        elif type(toR)==TitleState:
            self.renderTitle(toR.title)
    def clearLayout(self):
        while self.layout_.count():
            if tmp:=self.layout_.takeAt(0):
                if tmp:= tmp.widget():
                    tmp.setParent(None)
    def renderTitle(self,t:Title):
        self.textDisplay.setText('<h1>'+t.title+'</h1>' # <h1/h2?>
                                 +'<h2>'+t.subTitle+'<h2>'
                                 )
        self.layout_.addWidget(self.textDisplay)
        self.textDisplay.show()
        self.adjustBorders()
        self.adjustFontSize()
        self.handleInvert()
    def renderImage(self,image:Image):
        self.textDisplay.setText("")
        #self.textDisplay.setPixmap(QPixmap(image.path))
        self.layout_.addWidget(self.textDisplay)
        self.textDisplay.show()
        self.adjustBorders()
        self.adjustImgSize(image)
        pass
    def adjustImgSize(self,image:Image):
        m=self.state.margins
        wMax=int(self.width()*1*(1-m.left-m.right))
        hMax=int(self.height()*1*(1-m.top-m.bottom))
        self.textDisplay.setPixmap(QPixmap(image.path).scaled(wMax,hMax,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))


    def renderVerse(self,verse:str):
        verse=verse.strip()
        verse=verse.replace('\n','<br/>')
        self.textDisplay.show()
        self.layout_.addWidget(self.textDisplay)
        self.textDisplay.setText(verse)
        self.adjustBorders()
        self.adjustFontSize()
        self.handleInvert()
    def addBridge(self,b:QtBridge):
        self.bridge=b
        self.bridge.stateUpdated.connect(self.renderState)
    def adjustBorders(self):
        m=self.state.margins
        self.layout_.setContentsMargins(
                int((m.left)*self.width()),
                int(m.top*self.height()),
                int((m.right)*self.width()),
                int(m.bottom*self.height()))
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
        if a0 and a0.key() == Qt.Key.Key_F1:
            self.adjustFontSize()
        if a0 and a0.key() == Qt.Key.Key_F2:
            self.state._state.print()
    def handleInvert(self):
        backgroundColor="white"
        textColor="black"
        if self.state._opts.inversion:
            backgroundColor,textColor=textColor,backgroundColor
        self.textDisplay.setStyleSheet("background-color: "+backgroundColor+"; color: "+textColor+";")
    def resizeEvent(self, a0):
        s=self.state.getBonnomState()
        if isinstance(s,SongState):
            self.adjustFontSize()
        elif isinstance(s,ImageState):
            self.adjustImgSize(s.image)
        super().resizeEvent(a0)
    def adjustFontSize(self):
        font = self.textDisplay.font()
        font.setPointSize(1)#??
        self.textDisplay.setFont(font)#??
        m=self.state.margins
        wMax=int(self.width()*0.9*(1-m.left-m.right))
        hMax=int(self.height()*0.9*(1-m.top-m.bottom))
        low, high = 1, 500
        while low<high:
            mid = (low + high+1) // 2
            font.setPointSize(mid)
            rect =  html_bounding_rect(self.textDisplay.text(),font)
            if rect.width() <= wMax and rect.height ()<=hMax:
                 low=mid
            else:
                 high=mid-1
        font.setPointSize(low)
        self.textDisplay.setFont(font)
