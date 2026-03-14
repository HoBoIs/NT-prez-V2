from typing import Callable
import os
from PyQt6.QtWidgets import QCheckBox, QFrame,  QGridLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer, Qt
from state.config import Config
from state.talk import Talk, TalkMedia, makeFakeTalk
from state.template import Template
from state.topState import TopState, dataContainer
from PyQt6.QtWidgets import QSizePolicy
from display.mediaType import detectMediaType
from display.utils import DragHandle, ListEditHless,ListEdit, ListItem,ReorderContainer,NoWheelComboBox,SaveBtns


class RollableListEditor(QWidget):
    contents:list[NoWheelComboBox]
    scrollA : QScrollArea
    layout_:QVBoxLayout
    cont: QWidget
    images:list[str]
    updater:Callable
    def __init__(self,imgs:list[str],selectedImg:list[str],updater:Callable):
        super().__init__()
        self.contents=[]
        self.updater=updater
        
        mainLayout = QVBoxLayout(self)

        self.scrollA = QScrollArea()
        mainLayout.addWidget(self.scrollA)
        mainLayout.setContentsMargins(0,0,0,0)
        self.cont=QWidget()
        self.layout_=QVBoxLayout(self.cont)
        self.layout_.setContentsMargins(0,0,0,0)
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_.setSpacing(0)
        self.scrollA.setWidget(self.cont)
        self.images=imgs
        for im in selectedImg:
            self.addBox(im)
        self.addBox()
        self.scrollA.setWidgetResizable(True)
        self.setMaximumHeight(64)
        self.setMaximumWidth(8000)

        self.scrollA.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollA.setFrameShape(QScrollArea.Shape.NoFrame)
        #for im in selectedImg:
        #    self.contents[-1].setCurrentText(im)
    def setImages(self,selectedImg):
        self.removeBoxes()
        for im in selectedImg:
            self.addBox(im)
        self.addBox()
    def removeBoxes(self):
        for s in self.contents:
            self.layout_.removeWidget(s)
        self.contents=[]
    def addBox(self,s:str=""):
        self.contents.append(NoWheelComboBox())
        self.contents[-1].addItems([""])
        self.contents[-1].addItems(self.images)
        self.layout_.addWidget(self.contents[-1])
        self.contents[-1].setCurrentText(s)
        self.contents[-1].currentIndexChanged.connect(
            lambda _, i=len(self.contents)-1: self.onChanged(i)
        )
        self.contents[-1].currentIndexChanged.connect(self.updater)
        self.contents[-1].setMaximumHeight(20)
        self.contents[-1].setMinimumWidth(20)
        QTimer.singleShot(20, self.scroll_to_bottom)
    def onChanged(self, idx):
        if idx == len(self.contents)-1:
            if self.contents[idx].currentText()!="":
                self.addBox()
        elif self.contents[idx].currentText()=="":
            for i in range(idx+1,len(self.contents)):
                self.layout_.removeWidget(self.contents[i])
            self.contents=self.contents[0:idx+1]
    def scroll_to_bottom(self):
        bar = self.scrollA.verticalScrollBar()
        if bar:
            bar.setValue(bar.maximum())
    def getImages(self):
        return [c.currentText() for c in self.contents[:-1]] 

class MediaEditor(QWidget):
    chooser: NoWheelComboBox
    layout_: QGridLayout
    col: int
    chb: QCheckBox
    special:QPushButton
    mediaDir:str
    paths:list[str]
    def __init__(self,l:QGridLayout, col:int, paths:list[str], selected:TalkMedia,updater:Callable):
        super().__init__()
        self.paths=paths
        self.layout_=l
        self.col=col
        self.chooser=NoWheelComboBox()
        self.chooser.setMinimumWidth(16)
        self.layout_.addWidget(self.chooser,0,col,1,2)
        self.chooser.addItems([""]+paths)
        s=selected.path.split("/")[-1]
        self.mediaDir=selected.path.removesuffix(s)
        if selected.path and s in paths:
            self.chooser.setCurrentText(s)
        self.chb=QCheckBox("Autoplay")
        self.layout_.addWidget(self.chb,1,col)
        self.special=QPushButton("⚙️")
        if selected.autoPlay:
            self.chb.setChecked(True)
        self.special.setMinimumWidth(16)
        self.layout_.addWidget(self.special,1,col+1)
        self.chooser.currentIndexChanged.connect(updater)
        self.chb.stateChanged.connect(updater)
    def set(self,selected:TalkMedia):
        s=selected.path.split("/")[-1]
        if selected.path and s in self.paths:
            self.chooser.setCurrentText(s)
        if selected.autoPlay:
            self.chb.setChecked(True)

    def getMedia(self):
        path=self.mediaDir+self.chooser.currentText()
        if self.chooser.currentText():
            isMusic=detectMediaType(self.mediaDir+self.chooser.currentText())=="audio"#TODO override from special
        else:
            isMusic=True

        return TalkMedia(
                path=path,
                isMusic=isMusic,
                autoPlay=self.chb.isChecked(), 
                musicSong=""#TODO from special
                )
        




class ThxChooser():
    typeIn:NoWheelComboBox
    layout_: QGridLayout
    templates:list[Template]
    nameIns: list[QLineEdit]
    oldT:tuple[Template,list[str]]
    nameMemory:list[str]
    col:int
    updater:Callable
    def __init__(self,t:tuple[Template,list[str]],l:QGridLayout,col:int,ts:list[Template],updater:Callable):
        self.updater=updater
        #self.layout_=QGridLayout(self)
        #self.setLayout(self.layout_)
        self.col=col
        self.oldT=t
        self.layout_=l
        self.templates=ts
        self.typeIn=NoWheelComboBox()
        self.typeIn.setMinimumWidth(20)
        self.typeIn.addItems(["Nincs"])
        self.typeIn.addItems([ta.titles[0] for ta in ts])
        self.nameMemory=["",""]
        for i,t0 in enumerate(ts):
            if t[0]==t0:
                self.typeIn.setCurrentIndex(i+1)
        names=t[1]
        if self.oldT[0].params:
            while len(names)<self.oldT[0].params[0]:
                names.append("")
        self.nameIns=[QLineEdit(n.strip()) for n in names]
        for s in self.nameIns:  
            s.textEdited.connect(self.updater)
        if self.oldT[0].params:
            for i in range(self.oldT[0].params[0]):
                self.layout_.addWidget(self.nameIns[i],1,self.col+i,1,3-self.oldT[0].params[0])
        self.layout_.addWidget(self.typeIn,0,self.col,1,2)
        self.typeIn.currentIndexChanged.connect(
                lambda _:self.onChangedBox()
                )
        self.updater=updater
        self.typeIn.currentIndexChanged.connect(updater)
    def initFields(self,t:tuple[Template,list[str]]):
        for i,t0 in enumerate(self.templates):
            if t[0]==t0:
                self.typeIn.setCurrentIndex(i+1)
        names=t[1]
        self.nameMemory=(names+["",""])[:2]
        for i in range(len(self.nameIns)):
            self.nameIns[i].setText(self.nameMemory[i])


    def onChangedBox(self):
        cnt=0
        title=self.typeIn.currentText()
        for t in self.templates:
            if t.titles[0]==title:
                cnt=t.params[0]
        for w in self.nameIns:
            self.layout_.removeWidget(w)
        while len(self.nameIns)>cnt:
            self.nameMemory[len(self.nameIns)-1]=self.nameIns[-1].text()
            self.nameIns=self.nameIns[:-1]
        while len(self.nameIns)<cnt:
            self.nameIns.append(QLineEdit(self.nameMemory[len(self.nameIns)]))
            self.nameIns[-1].textEdited.connect(self.updater)
        for i in range(cnt):
            self.layout_.addWidget(self.nameIns[i],1,self.col+i,1,3-cnt)
        

    def getThx(self):
        title=self.typeIn.currentText()
        if title=="Nincs":
            return (Template([],[],[],-1),[])
        t=self.templates[self.typeIn.currentIndex()-1]
        names=[i.text() for i in self.nameIns]
        return (t,names)


class TalkEdit(ListItem):
    titleIn: QLineEdit
    name1In: QLineEdit
    name2In: QLineEdit
    thxIn: ThxChooser
    imagesIn: RollableListEditor
    #imagesIn: DynamicComboWidget
    mediaIn: MediaEditor
    oldTalk:Talk
    data:dataContainer
    oss:Callable
    def __init__(self, t:Talk,data:dataContainer, conf:Config,onSaveState:Callable):
        super().__init__()
        self.oss=onSaveState
        self.data=data
        self.oldTalk=t
        #self.layout_.setHorizontalSpacing(0)
        for i,w in enumerate([1,3,2,2,2,4,3,1,2]):
            self.layout_.setColumnStretch(i,w)
        self.layout_.addWidget(self.handle,0,0,2,1)
        self.titleIn=QLineEdit()
        self.layout_.addWidget(self.titleIn,0,1)
        self.name1In=QLineEdit()
        self.name2In=QLineEdit()
        self.layout_.addWidget(self.name1In,0,2)
        self.layout_.addWidget(self.name2In,1,2)
        self.thxIn=ThxChooser(t.thanks,self.layout_,3,list(data.templstes.values()),self.onChange)
        self.imagesIn=RollableListEditor(
                [d.path.split('/')[-1] for d in data.images],
                t.pictures,
                self.onChange) #t.pictures
        self.layout_.addWidget(self.imagesIn,0,5,2,1)
        self.mediaIn=MediaEditor(self.layout_,6,os.listdir(conf.talkMediaDir),t.media,self.onChange) #t.mediaPath, t.musicSong
        self.layout_.addWidget(self.saver,0,8,2,1)
        self.titleIn.textEdited.connect(self.onChange)
        self.name1In.textEdited.connect(self.onChange)
        self.name2In.textEdited.connect(self.onChange)
        self.initFields()
    def getTalk(self):
        n1=self.name1In.text().strip()
        n2=self.name2In.text().strip()
        return Talk(
            title=self.titleIn.text(),
            name=n1 + (" & " + n2 if n2 else ""),
            thanks=self.thxIn.getThx(),
            media=self.mediaIn.getMedia(),
            pictures=self.imagesIn.getImages(),
            _id=self.oldTalk._id,
            orderIDX=self.oldTalk.orderIDX
        )
    def initFields(self):
        self.titleIn.setText(self.oldTalk.title)
        names=self.oldTalk.name.split('&')
        if len(names) == 1:
            names.append("")
        self.name1In.setText(names[0].strip())
        self.name2In.setText(names[1].strip())
        self.thxIn.initFields(self.oldTalk.thanks)
        self.imagesIn.setImages(self.oldTalk.pictures)
        self.mediaIn.set(self.oldTalk.media)
    def isChanged(self)->bool:
        tmp=self.getTalk()
        tmp._id=self.oldTalk._id
        tmp.orderIDX=self.oldTalk.orderIDX
        return self.oldTalk!=tmp
    def getID(self) -> int:
        return self.oldTalk._id
    def setID(self,v):
        self.oldTalk._id=v
    def onChange(self):
        self.updateSaveBtns()
        self.onChangedData.emit()
    def setOrder(self, v: int) -> None:
        self.oldTalk.orderIDX=v
    def save(self):
        newTalk=self.getTalk()
        self.data.talks[self.oldTalk._id]=newTalk
        self.oldTalk=newTalk
        self.onChange()
        self.oss()
    def cancelEdit(self):
        self.initFields()
        self.onChange()


class TalkHeader(QWidget):
    layout_: QGridLayout
    def __init__(self):
        super().__init__()
        self.container=QWidget()
        self.layout_=QGridLayout(self.container)
        self.setLayout(self.layout_)
        for i,w in enumerate([1,3,2,2,2,4,3,1,2]):
            self.layout_.setColumnStretch(i,w)
        self.layout_.addWidget(QLabel(""),0,0)
        self.layout_.addWidget(QLabel("Cím"),0,1)
        self.layout_.addWidget(QLabel("Név/nevek"),0,2)
        self.layout_.addWidget(QLabel("Köszönöjük"),0,3,1,2)
        self.layout_.addWidget(QLabel("Képek"),0,5)
        self.layout_.addWidget(QLabel("Bev. utáni zene/videó"),0,6)
        self.layout_.addWidget(QLabel("SAVE"),0,8)
        #self.layout_.addWidget(SaveBtns(),0,8)


class TalkListEdit(ListEdit):
    state:TopState
    os:Callable
    def __init__(self, parent: QWidget|None, s:TopState,c:Callable) :
        self.state=s
        self.os=c
        super().__init__(parent,TalkHeader(),
                         ListEditHless(None,[TalkEdit(t,s.data,s.cfg,c) for t in s.data.talks.values()],
                                       lambda: TalkEdit(makeFakeTalk()  ,s.data,s.cfg,c)))
