from PyQt6.QtWidgets import QApplication, QGraphicsScene, QMainWindow, QVBoxLayout, QWidget, QGraphicsView
from PyQt6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    scene:QGraphicsScene
    view:QGraphicsView
    def __init__(self):
        super().__init__()
        self.scene=QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
    pass
app = QApplication(sys.argv)
mainWindow = QWidget()
mainWindow.show()  
from state import State
s=State(mainWindow=mainWindow)
s.text.setText("123 \n\n *456*")
s.text.setTextFormat(s.Tformat)
layout=QVBoxLayout()
layout.addWidget(s.text)
mainWindow.setLayout(layout)
#mainWindow.paintEngine()

app.exec()
#s.foo()
