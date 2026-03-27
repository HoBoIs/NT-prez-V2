from PyQt6.QtWidgets import QWidget
from state.topState import TopState


class StatusViewer(QWidget):
    ts:TopState
    def __init__(self,ts:TopState , parent: QWidget|None) -> None:
        super().__init__(parent)
        self.ts=ts

