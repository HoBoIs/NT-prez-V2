from typing import Callable, List
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from typing import TypeVar,Generic
from PyQt6.QtGui import QMouseEvent, QDrag,QCursor
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
    p:'ListEditHless'
    def __init__(self, p : 'ListEditHless'):
        super().__init__()
        self.setAcceptDrops(True)
        self.layout_=QVBoxLayout(self)
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout_.setContentsMargins(0,0,0,0)
        self.draggedWidget = None
        self.last = None
        self.p=p
    def addWidget(self, w:QWidget):
        self.last=w
        self.layout_.addWidget(w)
        self.setOrders()
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
        self.setOrders()
        a0.accept()
    def isLast(self,w:QWidget):
        return w is self.last
    def setOrders(self):
        items = [self.layout_.itemAt(i) for i in range(self.layout_.count())]
        widgets = [i.widget() for i in items if i and i.widget()]
        idx=1
        for w in widgets:
            if isinstance(w,ListItem) and not self.isLast(w):
                w.handle.setNumber(idx)
                idx+=1


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
        mime.setText("reorder with drag")
        drag.setMimeData(mime)
        pixmap=widget.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(widget.mapFromGlobal(QCursor.pos()))
        drag.exec(Qt.DropAction.MoveAction)
    def setNumber(self,i:int):
        super().setText('≡ {:3d}'.format(i))

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
    toDelete:bool
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
        self.toDelete=False
        self.saver.acceptBtn.pressed.connect(self.save)
        self.saver.cancelBtn.pressed.connect(self.cancelEdit)
        self.saver.deleteBtn.pressed.connect(self.markForDelete)
    def markForDelete(self):
        self.toDelete=True
        for i in range(self.layout_.count()):
            tmp= self.layout_.itemAt(i)
            c = tmp.widget() if tmp else None
            if c!=None and (c not in [self.saver]):
                effect = QGraphicsOpacityEffect(c)
                effect.setOpacity(0.1)
                c.setGraphicsEffect(effect)
                print(tmp,'--',c)
            else:
                print(tmp,'--',c)
        self.updateSaveBtns()
        pass
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
    def saveUpdate(self) -> bool:
        pass
    def save(self):
        if self.toDelete:
            self.callDelete()
            return
        if self.saveUpdate():
            self.updateSaveBtns()
            self.callEditorToSave()
    @abstractmethod
    def restore(self):
        pass
    def cancelEdit(self):
        self.restore()
        self.toDelete=False
        for i in range(self.layout_.count()):
            tmp= self.layout_.itemAt(i)
            c = tmp.widget() if tmp else None
            if c!=None:
                c.setGraphicsEffect(None)
        self.updateSaveBtns()
    def callDelete(self):
        p=self.parent()
        if isinstance(p,ReorderContainer):
            p.layout_.removeWidget(self)
            self.callEditorToSave()
            self.deleteLater()
            p.setOrders()

    def updateSaveBtns(self):
        self.changed=self.isChanged()
        self.saver.setChanged(self.changed)
    def callEditorToSave(self):
        p=self.parent()
        assert isinstance(p,ReorderContainer)
        pp=p.p
        pp.callEditorToSave(self)
        



MyWidget= TypeVar("MyWidget",bound=ListItem)
class ListEditHless(QScrollArea,Generic[MyWidget]):
    container : ReorderContainer
    makeLast:Callable[[],MyWidget]
    last:MyWidget
    childs:list[MyWidget]
    def __init__(self, parent: QWidget | None, childs :List[MyWidget], makeLast:Callable[[],MyWidget] ):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.container = ReorderContainer(self)
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
    def getWidgets(self)->list[ListItem]:
        items = [self.container.layout_.itemAt(i) for i in range(self.container.layout_.count())]
        widgets = [i.widget() for i in items if i and i.widget()]
        widgets = [w for w in widgets if isinstance(w,ListItem)]
        return widgets
    def callEditorToSave(self,caller:ListItem):
        p=self.parent()
        assert isinstance(p,ListEdit)
        p.saveEvent(caller)



    


class ListEdit(QWidget):
    layout_:QVBoxLayout
    d:ListEditHless
    def __init__(self, parent: QWidget|None, header:QWidget, data:ListEditHless ) :
        super().__init__(parent)
        self.d=data
        self.layout_=QVBoxLayout(self)
        self.layout_.addWidget(header)
        self.layout_.addWidget(data)
    def getWidgets(self)->list[ListItem]:
        return self.d.getWidgets()
    def saveEvent(self,caller:ListItem):
        pass
