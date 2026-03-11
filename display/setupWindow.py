from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QCheckBox, QComboBox, QCompleter, QGridLayout, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget, QLabel
from state.topState import TopState, dataContainer
from display.utils import DragHandle,ReorderContainer,SaveBtns,NoWheelComboBox
from display.talkEdit import TalkEdit
from state.config import Config
from PyQt6.QtCore import QSortFilterProxyModel, QStringListModel, Qt
import unicodedata
from PyQt6.QtGui import QKeySequence, QGuiApplication
import re

class PasteAwareLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
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

class FilterableComboBox(NoWheelComboBox):
    proxy_model:QSortFilterProxyModel
    completer_:QCompleter
    _lineEdit:QLineEdit
    def __init__(self, parent=None, items:list=[tuple[str,...]]):
        super().__init__(parent)
        
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        self.proxy_model = NormalizedProxyModel(self)
        self.proxy_model.setSourceModel(self.model())

        self.completer_ = QCompleter(self.proxy_model, self)
        self.completer_.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.setCompleter(self.completer_)
        self._lineEdit=PasteAwareLineEdit(self)
        self.setLineEdit(self._lineEdit)
        self._lineEdit.textEdited.connect(self.proxy_model.setFilterFixedString)
        for i in items:
            self.add_item_with_data(i[0],i[1])
        self.setCurrentText("")

    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated.emit(self.currentIndex())

    def add_item_with_data(self, text, obj):
        self.addItem(text, obj)


class ItemEdit(QWidget):
    layout_: QGridLayout
    handle: DragHandle
    nameIn: NoWheelComboBox
    kindIn: NoWheelComboBox
    wasBefore: QCheckBox
    placeHolder: QLabel
    viewer: QPushButton
    saver : SaveBtns
    data:dataContainer
    container: QWidget

    categories:list[str]
    items:list
    def handle_multiline_paste(self,lines):
        self.nameIn.setCurrentText(self.nameIn.currentText()+lines[0])
        if len(lines)==1:
            return
        container = self.parentWidget()
        if isinstance(container, SongOrderEditor):
            index = container.layout_.indexOf(self)

            for i, line in enumerate(lines[1:], start=1):
                new_widget = container.create_row(line)
                container.layout_.insertWidget(index + i, new_widget)
            if container.layout_.count()==index+len(lines):
                new_widget = container.create_row("")
                container.layout_.addWidget( new_widget)

    def __init__(self, data:dataContainer, conf:Config):
        super().__init__()
        self.data=data
        self.container=QWidget()
        self.layout_=QGridLayout(self.container)
        self.setLayout(self.layout_)
        for i,w in enumerate([1,5,3,1,3,2,2]):
            self.layout_.setColumnStretch(i,w)
        self.handle=DragHandle()
        self.layout_.addWidget(self.handle,0,0)
        #self.nameIn=FuzzyComboBox([("|".join( s.titles),s,"Song") for s in data.songs.values()])
        self.nameIn=FilterableComboBox(self,[("|".join( s.titles),s,"Song") for s in data.songs.values()])
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
        self.saver=SaveBtns()
        self.layout_.addWidget(self.saver,0,6)

class SongOrderEditor(ReorderContainer):
    data:dataContainer
    conf:Config
    def __init__(self,d,c):
        super().__init__()
        self.data=d
        self.conf=c
        self.layout_.addWidget(self.create_row())

    def create_row(self, text=""):
        tmp=ItemEdit(self.data,self.conf)
        if text:
            tmp.nameIn.setCurrentText(text)
        return tmp
    
    



class SetupWindow(QWidget):
    layout_: QGridLayout
    state:TopState
    items:list[TalkEdit]
    def __init__(self, s:TopState):
        super().__init__()
        self.state=s
        self.layout_=QGridLayout(self)
        self.setLayout(self.layout_)
        self.items=[]
        i=0
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.container = ReorderContainer()
        scroll.setWidget(self.container)
        self.layout_.addWidget(scroll,0,0)
        #soe=ItemEdit(s.data,self.state.cfg)
        self.so=SongOrderEditor(s.data,self.state.cfg)
        scroll2 = QScrollArea()
        scroll2.setWidgetResizable(True)
        scroll2.setWidget(self.so)
        
        self.layout_.addWidget(scroll2,0,1)
        for t in s.data.talks.values():
            self.container.addWidget(TalkEdit(t,s.data,self.state.cfg))
            
            #self.layout_.addWidget(self.items[-1],i,0)
            #i+=1
