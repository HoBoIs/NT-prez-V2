from PyQt6.QtGui import QMouseEvent, QDrag
from PyQt6.QtCore import QTimer, Qt,QMimeData
from PyQt6.QtWidgets import QCheckBox, QComboBox, QGridLayout, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget, QLabel
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
        pos=a0.position().toPoint()
        tIdx=max(self.layout_.count()-2,1)
        for i in range(1,self.layout_.count()-2):
            item= self.layout_.itemAt(i)
            if not item :
                continue
            w=item.widget()
            if w is self.draggedWidget or w ==None:
                continue
            if pos.y() < w.geometry().center().y():
                tIdx=i
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
