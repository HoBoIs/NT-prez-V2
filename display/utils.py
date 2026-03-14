from typing import Callable, List
from typing import TypeVar,Generic
from PyQt6.QtGui import QMouseEvent, QDrag
from PyQt6.QtCore import QObject, QTimer, Qt,QMimeData, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QFrame,QComboBox, QGridLayout, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QWheelEvent

class SaveBtns(QWidget):
    deleteBtn:QPushButton
    acceptBtn:QPushButton
    cancelBtn:QPushButton
    changed:bool
    layout_:QGridLayout
    def __init__(self):
        super().__init__()
        self.deleteBtn=QPushButton("🗑️")
        self.acceptBtn=QPushButton("✅")
        self.cancelBtn=QPushButton("❌")
        self.layout_=QGridLayout(self)
        self.setLayout(self.layout_)
        self.acceptBtn.setMinimumWidth(15)
        self.cancelBtn.setMinimumWidth(15)
        self.deleteBtn.setMinimumWidth(30)
        self.layout_.addWidget(self.deleteBtn,0,0,1,2)
        self.layout_.addWidget(self.acceptBtn,0,0)
        self.layout_.addWidget(self.cancelBtn,0,1)
        self.cancelBtn.setVisible(False)
        self.acceptBtn.setVisible(False)
        self.changed=False
    def setChanged(self,b:bool):
        self.changed=b
        self.cancelBtn.setVisible(self.changed)
        self.acceptBtn.setVisible(self.changed)
        self.deleteBtn.setVisible(not self.changed)
class NoWheelComboBox(QComboBox):
    def wheelEvent(self, e: QWheelEvent | None):
        if e==None:
            return
        e.ignore()  
class ReorderContainer(QWidget):
    layout_:QVBoxLayout
    draggedWidget:None|QWidget
    last:QWidget | None
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.layout_=QVBoxLayout(self)
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_.setContentsMargins(0,0,0,0)
        self.draggedWidget = None
        self.last = None
    def addWidget(self, w:QWidget):
        self.last=w
        self.layout_.addWidget(w)
    def dragEnterEvent(self, a0):
        if a0:
            a0.accept()

    def dragMoveEvent(self, a0):
        if a0:
            a0.accept()
    def dropEvent(self, a0):
        if not self.draggedWidget:
            return
        if not a0:
            return
        under=False
        pos=a0.position().toPoint()
        tIdx=max(self.layout_.count()-2,0)
        for i in range(self.layout_.count()-2):
            item= self.layout_.itemAt(i)
            if not item :
                continue
            w=item.widget()
            if (w is self.draggedWidget) or w ==None:
                under=True
                continue
            if pos.y() < w.geometry().center().y():
                tIdx=i
                if under:
                    tIdx-=1
                break #TODO better search
        self.layout_.removeWidget(self.draggedWidget)
        self.layout_.insertWidget(tIdx, self.draggedWidget)
        self.draggedWidget = None
        a0.accept()
    def isLast(self,w:QWidget):
        return w is self.last

class DragHandle(QLabel):
    def __init__(self, parent=None):
        super().__init__("≡", parent)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, ev:QMouseEvent| None ):
        if ev==None:
            return
        self.startPos = ev.pos()

    def mouseMoveEvent(self, ev:QMouseEvent| None):
        if ev==None:
            return
        if (ev.pos() - self.startPos).manhattanLength() < 4:
            return
        widget = self.parentWidget()
        if not widget:
            return
        container = widget.parentWidget()
        if not isinstance(container,ReorderContainer):
            return
        if container.isLast(widget):
            return
        container.draggedWidget = widget

        drag = QDrag(self)
        mime = QMimeData()
        mime.setText("reorder")
        drag.setMimeData(mime)

        drag.exec(Qt.DropAction.MoveAction)
from abc import ABCMeta, abstractmethod
from typing import Type, Any, cast
QABCMeta = cast(Type[Any], type("QABCMeta", (type(QObject), ABCMeta), {}))

class ListItem(QFrame,metaclass=QABCMeta):
    layout_: QGridLayout
    container: QWidget
    saver : SaveBtns
    changed: bool
    handle: DragHandle
    onChangedData = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.container=QWidget()
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.layout_=QGridLayout(self.container)
        self.setLayout(self.layout_)
        self.saver=SaveBtns()
        self.handle=DragHandle()
        self.changed=False
        self.saver.acceptBtn.pressed.connect(self.save)
        self.saver.cancelBtn.pressed.connect(self.cancelEdit)

    @abstractmethod
    def isChanged(self)->bool:
        pass
    @abstractmethod
    def getID(self)->int:
        pass
    @abstractmethod
    def setID(self,v:int)->None:
        pass
    @abstractmethod
    def setOrder(self,v:int)->None:
        pass
    @abstractmethod
    def save(self):
        pass
    @abstractmethod
    def cancelEdit(self):
        pass
    def updateSaveBtns(self):
        self.changed=self.isChanged()
        self.saver.setChanged(self.changed)



MyWidget= TypeVar("MyWidget",bound=ListItem)
class ListEditHless(QScrollArea,Generic[MyWidget]):
    container : ReorderContainer
    makeLast:Callable[[],MyWidget]
    last:MyWidget
    childs:list[MyWidget]
    def __init__(self, parent: QWidget | None, childs :List[MyWidget], makeLast:Callable[[],MyWidget] ):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.container = ReorderContainer()
        self.setWidget(self.container)

        for w in childs:
            self.container.addWidget(w)
        self.makeLast=makeLast
        self.last=makeLast()
        self.childs=childs
        self.container.addWidget(self.last)
        self.last.onChangedData.connect(self.onLastEdited)
    def onLastEdited(self):
        self.last.onChangedData.disconnect()
        if self.childs:
            newId=1+max([t.getID() for t in self.childs])
        else:
            newId=0
        self.last.setID(newId)
        self.last.setOrder(len(self.childs))
        self.childs.append(self.last)
        self.last=self.makeLast()
        self.last.onChangedData.connect(self.onLastEdited)
        self.container.addWidget(self.last)


    


class ListEdit(QWidget):
    layout_:QVBoxLayout
    def __init__(self, parent: QWidget|None, header:QWidget, data:QWidget ) :
        super().__init__(parent)
        self.layout_=QVBoxLayout(self)
        self.layout_.addWidget(header)
        self.layout_.addWidget(data)
