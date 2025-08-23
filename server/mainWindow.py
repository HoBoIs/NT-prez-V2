from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsTextItem, QMainWindow, QVBoxLayout, QWidget, QGraphicsView
from displayWindow import DisplayWindowData
from collections.abc import Callable, Awaitable
from PyQt6.QtCore import QTimer, QUrl, Qt
import sys
from dataclasses import dataclass
import PyQt6.QtMultimedia as QtMultimedia
import PyQt6.QtCore as QtCore 
from PyQt6.QtMultimediaWidgets import QVideoWidget
import PyQt6.QtGui as QtGui
import PyQt6.QtQuick as QtQuick
from PyQt6.QtWidgets import QGraphicsScene, QLabel, QWidget
from PyQt6.QtGui import QFont, QKeyEvent, QPaintDevice, QPainter, QTransform,QColor
from song import SongListState
from util import connectOnce
from talk import TalkState
def skip():
    pass
app = QApplication(sys.argv)
@dataclass
class MainWindow(QMainWindow):
    scene:QGraphicsScene
    view:QGraphicsView
    data : DisplayWindowData
    mediaPlayer: QtMultimedia.QMediaPlayer
    videoPlayer:QVideoWidget 
    imageDispay = QtGui.QImage()
    textDisplay =QGraphicsTextItem()
    maxSongFont=100
    maxTalkFont=80
    maxScale=1.0
    margins=[0.05,0.05,0.05,0.05]#left,top,right,bottom
    isInverted=False
    audioDevice :QtMultimedia.QAudioOutput
    
    def __init__(self):
        super().__init__()
        self.mediaPlayer = QtMultimedia.QMediaPlayer(self)
        self.videoPlayer= QVideoWidget(self)
        self.data=DisplayWindowData(self)
        self.scene=QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scene.addItem(self.textDisplay)
        self.audioDevice=QtMultimedia.QAudioOutput()
        self.audioDevice.setMuted(False)
        self.audioDevice.setVolume(0.5)
        self.mediaPlayer.setAudioOutput(self.audioDevice)
        self.mediaPlayer.setVideoOutput(self.videoPlayer)
        self.videoPlayer.hide()
    endMusic:Callable
    def afterMusic(self,p):
        self.endMusic()
        self.videoPlayer.hide()
    def startMusic2(self,*p):
        connectOnce(self.mediaPlayer.playingChanged,self.afterMusic,lambda x: not x)
        self.mediaPlayer.play()
        
    def playMusic(self,musicPath:str,atEnd: Callable[[],None] = skip):
        if (musicPath==""):
            return
        self.endMusic=atEnd
        if (self.mediaPlayer.source()!=QUrl(musicPath)):
            connectOnce(self.mediaPlayer.sourceChanged,self.startMusic2)
            self.mediaPlayer.setSource(QUrl(musicPath))
        else: 
            self.mediaPlayer.setSource(QUrl(musicPath))
            self.startMusic2()
    timer :QTimer
    def delayed(self,t,fun):
        connectOnce(self.timer.timeout,fun)
        self.timer.start(t*1000)
    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.mediaPlayer.isPlaying():
            self.mediaPlayer.pause()
    def stop(self):
        #self.audioPlayer.playingChanged.disconnect()
        #self.videoPlayer .playingChanged.disconnect()
        self.videoPlayer.hide()
        pass
    def playVideo(self,videoPath:str,atEnd:Callable[[],None]):
        if (videoPath==""):
            return
        self.endMusic=atEnd
        if (self.mediaPlayer.source()!=QUrl(videoPath)):
            connectOnce(self.mediaPlayer.sourceChanged,self.startMusic2)
            self.mediaPlayer.setSource(QUrl(videoPath))
        else: 
            self.mediaPlayer.setSource(QUrl(videoPath))
            self.startMusic2()
        pass
    def displayImage(self,imagePath:str):
        
        pass
    def displayVerse(self,verse:str):
        if verse=="":
            self.textDisplay.setHtml("")
            return
        self.view.resetTransform()
        defaultFont=20
        self.textDisplay.setFont(QFont("Arial", defaultFont))
        self.textDisplay.setHtml('<div align="center">'+verse+"<\\div>")
        self.textDisplay.setPos(0,0)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textDisplay.setTextWidth(self.width())
        self.maxScale=self.maxSongFont/defaultFont
        transform = QTransform().scale(1, 1)
        self.view.setTransform(transform)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        print(self.view.size())

        self.resizeEvent(None)
        print(self.view.size())
    def adjustFontSize(self)->None:
        pass
        minFont=2
        maxFont=2048
        font=(minFont+maxFont)/2
        while (False):
            pass

    def resizeEvent(self, a0):

        self.textDisplay.adjustSize()
        bounds = self.textDisplay.boundingRect()
        maxLam=3
        lam=min(self.view.width()/bounds.width(),self.view.height()/bounds.height()) if bounds.width() else 1
        if lam<=maxLam:
            self.scene.setSceneRect(bounds.adjusted(-bounds.width() * self.margins[0], -bounds.height() *self.margins[1],
                                                           bounds.width() * self.margins[2], bounds.height() *self.margins[2]))
        else:
            l=maxLam/lam
            print(l)
            bounds.setWidth(bounds.width()*l)
            bounds.setHeight(bounds.height()*l)
            self.scene.setSceneRect(bounds.adjusted(-bounds.width() * self.margins[0], -bounds.height() *self.margins[1],
                                                           bounds.width() * self.margins[2],  bounds.height()* self.margins[2]))

        self.view.fitInView(self.view.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
        
        super().resizeEvent(a0)
    def invert(self):
        self.isInverted=not self.isInverted
        self.updateColors()
    def updateColors(self):
        self.textDisplay.setDefaultTextColor(QColor("white" if self.isInverted else "black"))
        self.scene.setBackgroundBrush(QColor("black" if self.isInverted else "white"))
    def keyPressEvent(self, a0 : QKeyEvent | None):
        if a0 !=None and a0.key() ==Qt.Key.Key_F11:
            self.swichFullScreen()
        if a0 !=None and a0.key() ==Qt.Key.Key_Plus:
            self.data.state.nextState()
            self.data.state.render()
        if a0 !=None and a0.key() ==Qt.Key.Key_Minus:
            self.data.state.prevState()
            self.data.state.render()
        if a0 !=None and a0.key() ==Qt.Key.Key_F9:
            self.displayVerse("111<br/>22<br/>3333asdasef as")
        if a0 !=None and a0.key() ==Qt.Key.Key_F8:
            self.data.state=SongListState(self)
            self.data.state.render()
        if a0 !=None and a0.key() ==Qt.Key.Key_F10:
            print(1)
            if type(self.data.state) == TalkState:
                print(2)
                self.data.state.startMusic()
        super().keyPressEvent(a0)
    def displayTalk(self, title:str, name:str):
        defaultFont=20
        self.textDisplay.setFont(QFont("Arial", defaultFont))
        self.textDisplay.setHtml('<h2 align="center">'+title+"<\\h2>"+'<h3 align="center">'+name+"<\\h3>")

        bounds = self.textDisplay.boundingRect()
        
        #self.textDisplay.setPos(-bounds.width()*s / 2, -bounds.height()*s / 2)
        self.scene.setSceneRect(bounds.adjusted(-bounds.width()*self.margins[0], -bounds.height()*self.margins[1],
                                                bounds.width()*self.margins[2], bounds.height()*self.margins[3]))
        self.view.fitInView(self.view.sceneRect(),Qt.AspectRatioMode.KeepAspectRatio)
        #self.textDisplay.setPos(0,0)
        #self.textDisplay.setTextWidth(self.width())
        #self.maxScale=self.maxTalkFont/defaultFont*10000
    def displayPicture(self,url:str, allawInvert:bool=False):
        pass
    def swichFullScreen(self):
        if not self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()
            

mainWindow = MainWindow()
mainWindow.show()  
mainWindow.displayVerse("első sor<br/>második<br/>hhharmadik<br/>hhharmadik");


app.exec()
#s.foo()
