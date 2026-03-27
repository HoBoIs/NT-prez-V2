from typing import Callable, Sequence
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QCheckBox, QComboBox, QCompleter, QGridLayout, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget, QLabel
from state.song import Song
from state.topState import TopState, dataContainer
from state.songOrderItem import SongOrderItem, SongOrderItemType
from display.utils import DragHandle, ListEdit, ListEditHless, ListItem,ReorderContainer,SaveBtns,NoWheelComboBox
from display.talkEdit import TalkEdit, TalkListEdit
from state.config import Config
from PyQt6.QtCore import QSortFilterProxyModel, QStringListModel, Qt
import unicodedata
from PyQt6.QtGui import QKeySequence, QGuiApplication
import re
class PasteAwareLineEdit(QLineEdit):
    def keyPressEvent(self, a0):
        if not a0:
            return

        if a0.matches(QKeySequence.StandardKey.Paste):
            if c:=QGuiApplication.clipboard():
                text = c.text()
            else:
                text=""

            if "\n" in text:
                lines = [l.strip() for l in text.splitlines() if l.strip()]

                if lines:
                    if p:=self.parentWidget():
                        grandparent = p.parentWidget()
                    else:
                        grandparent=None
                    if isinstance(grandparent,ItemEdit):
                        grandparent.handle_multiline_paste(lines)
                        return  
        super().keyPressEvent(a0)
class NormalizedProxyModel(QSortFilterProxyModel):
    _filter_text:str
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filter_text = ""
    def _normalize(self, text):
        if not text:
            return ""
        text = unicodedata.normalize('NFD', text.lower())
        text = re.sub(r'[^a-z0-9]', '', text)
        return text
    def setFilterFixedString(self, pattern):
        self._filter_text = self._normalize(pattern)
        super().invalidateFilter()
    def filterAcceptsRow(self, source_row, source_parent):
        s=self.sourceModel()
        if not s:
            return False
        index = s.index(source_row, 0, source_parent)
        item_text = s.data(index, Qt .ItemDataRole.DisplayRole)
        
        normalized_item = self._normalize(item_text)
        
        return self._filter_text in normalized_item

from state.talk import Talk
from state.song import Song
class FilterableComboBox(NoWheelComboBox):
    proxy_model:NormalizedProxyModel
    completer_:QCompleter
    _lineEdit:QLineEdit
    def __init__(self, parent:QWidget | None, items:Sequence[tuple[str,SongOrderItemType]],st:str):
        super().__init__(parent)
        self._lineEdit= PasteAwareLineEdit(self)
        self.setLineEdit(self._lineEdit)
        
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        self.proxy_model = NormalizedProxyModel(self)
        self.proxy_model.setSourceModel(self.model())

        self.completer_ = QCompleter(self.proxy_model, self)
        self.completer_.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.setCompleter(self.completer_)
        #self._lineEdit.textEdited.connect(self.proxy_model.setFilterFixedString)
        self._lineEdit.textEdited.connect(self.proxy_model.setFilterFixedString)
        was=False
        idx=0
        for i in items:
            self.add_item_with_data(i[0],i[1])
            if i[0]==st or  i[0].startswith(st+"|"):
                st=i[0]
                was=True
                self.setCurrentText(st)
                self.setCurrentIndex(idx)
                #self.getItem
            idx+=1
        if not was:
            self.setCurrentText("")

    def on_completer_activated(self, text:str):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated.emit(self.currentIndex())

    def add_item_with_data(self, text:str, obj):
        self.addItem(text, obj)


class ItemEdit(ListItem):
    nameIn: NoWheelComboBox
    kindIn: NoWheelComboBox
    wasBefore: QCheckBox
    placeHolder: QLabel
    viewer: QPushButton
    data:dataContainer

    categories:list[str]
    #items:list
    selected:tuple[str,None|SongOrderItemType]

    onSave:Callable
    def handle_multiline_paste(self,lines):
        self.nameIn.setCurrentText(self.nameIn.currentText()+lines[0])
        if len(lines)==1:
            return
        container = self.parentWidget()
        if isinstance(container, ReorderContainer):
            index = container.layout_.indexOf(self)

            for i, line in enumerate(lines[1:], start=1):
                new_widget = ItemEdit(self.data,self.conf,self.onSave)
                new_widget.nameIn.setCurrentText(line)
                container.layout_.insertWidget(index + i, new_widget)
            if container.layout_.count()==index+len(lines):
                new_widget = ItemEdit(self.data,self.conf,self.onSave)
                container.layout_.addWidget( new_widget)

    def __init__(self, data:dataContainer, conf:Config,onSave:Callable,st=""):
        super().__init__()
        self.onSave=onSave
        self.data=data
        self.selected=("",None)
        self.conf=conf
        for i,w in enumerate([1,5,3,1,3,2,2]):
            self.layout_.setColumnStretch(i,w)
        self.layout_.addWidget(self.handle,0,0)
        #self.nameIn=FuzzyComboBox([("|".join( s.titles),s,"Song") for s in data.songs.values()])
        self.nameIn=FilterableComboBox(self,[("|".join( s.titles),s) for s in data.songs.values()]+[(t.title,t) for t in data.talks.values()],st)
        if st:
            self.selected=self.getItem()
        self.nameIn.setMinimumWidth(30)
        #self.nameIn.setEditable(True)
        self.layout_.addWidget(self.nameIn,0,1)
        #for s in data.songs.values():
        #    self.nameIn.addItem( "|".join( s.titles),s  )

        self.kindIn=NoWheelComboBox()
        self.layout_.addWidget(self.kindIn,0,2)
        self.wasBefore=QCheckBox()
        self.layout_.addWidget(self.wasBefore,0,3)
        self.placeHolder=QLabel("TODO")
        self.layout_.addWidget(self.placeHolder,0,4)
        self.viewer=QPushButton("👁")
        self.layout_.addWidget(self.viewer,0,5)
        self.layout_.addWidget(self.saver,0,6)
        self.nameIn.currentTextChanged.connect(self.onChange)

    def getItem(self)->tuple[str,SongOrderItemType|None]:
        name=self.nameIn.currentText()
        index = self.nameIn.findText(name, Qt.MatchFlag.MatchExactly)
        data:SongOrderItemType|None
        if index >= 0:
            data =self.nameIn.itemData(index,Qt.ItemDataRole.UserRole)
        else:
            data=None
        return (name,data)
    def isChanged(self)->bool:
        return self.selected!=self.getItem()
    def getID(self)->int:#szerep ott lesz ha lesz verszsza-sorrend variálás
        if self.selected[1]:
            return 0
        return -1
    def setID(self,v:int)->None:#szerep ott lesz ha lesz verszsza-sorrend variálás
        pass
    def setOrder(self,v:int)->None:
        pass
    def save(self):
        if self.getItem()[1]:
            self.selected=self.getItem()
            self.updateSaveBtns()
            self.onSave()
    def cancelEdit(self):
        self.nameIn.setCurrentText(self.selected[0])
        pass
    def onChange(self):
        self.updateSaveBtns()
        self.onChangedData.emit()
    """def getConstructor(self):
        i=self.selected
        if i[1]:
            return makeConstructor(i[1])"""
        
class Header(QWidget):
    layout_: QGridLayout
    def __init__(self):
        super().__init__()
        self.container=QWidget()
        self.layout_=QGridLayout(self.container)
        self.setLayout(self.layout_)
        for i,w in enumerate([1,5,3,1,3,2,2]):
            self.layout_.setColumnStretch(i,w)
        self.layout_.addWidget(QLabel(""),0,0)
        self.layout_.addWidget(QLabel("Cím"),0,1)
        self.layout_.addWidget(QLabel("Típus"),0,2)
        self.layout_.addWidget(QLabel("TODO"),0,3,)
        self.layout_.addWidget(QLabel("TODO"),0,4)
        self.layout_.addWidget(QLabel("TODO"),0,5)
        self.layout_.addWidget(QLabel("SAVE"),0,6)

from state.songOrderIO import writeSongOrder
class SongOrderEditor(ListEdit):
    data:dataContainer
    conf:Config
    ls:list[ItemEdit]
    ts:TopState
    os:Callable
    def __init__(self,parent,d:dataContainer,c:Config,s:TopState, onSave:Callable):
        self.data=d
        self.ts=s
        self.conf=c
        self.ls=[ItemEdit(self.data,self.conf,self.writeToState,x.title) for x in d.songOrder]
        super().__init__(parent,Header(),
                         ListEditHless(None,self.ls,lambda: ItemEdit(self.data,self.conf,self.writeToState)
                         ))
        self.os=onSave
        
    def writeToState(self):
        res :list[SongOrderItemType|None] =[(s.getItem()[1]) for s in self.ls]
        res = [w.getItem()[1] for w in self.getWidgets() if isinstance(w,ItemEdit)]
        
        #for i,s in enumerate(self.ls):
        #    res+=[s.getConstructor()]
        with self.ts._lock:
            self.data.songOrder=[SongOrderItem (r) for r in res if r]
        #p=self.parent()
        #from display.setupWindow import SetupWindow
        #if isinstance(p,SetupWindow):
        #    p.sendUpdate()
        self.os()
        writeSongOrder("./res/songOrder.json",self.data.songOrder)
