import state.state as state
import state.topState as topState
from dataclasses import dataclass

@dataclass 
class Title:
    title:str
    subTitle:str

class TitleState(state.State):
    title:Title
    def nextState(self):
        self.notifyParentNxt()
    def prevState(self):
        self.notifyParentPrev()
    def __init__(self,ts : "topState.TopState | state.State",t:Title):
        super().__init__(ts)
        self.kind="TitleState"
        self.title=t
    def print(self):
        print(self.title)
        return super().print()
