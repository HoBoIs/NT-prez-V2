import state.state as state
import state.topState as topState
from dataclasses import dataclass

@dataclass
class Media:
    isMusic:bool
    atEndIdx:int
    path:str
    parent:"CustumState"#TODO use weekref to avoid memory-leaks


class CustumState(state.State):
    substates:list[state.State]
    idx:int
    media:Media | None
    def nextState(self):
        if self.childState:
            self.childState.nextState()
    def childEndedNxt(self):
        self.idx+=1
        if self.idx==len(self.substates):
            self.notifyParentNxt()
        else:
            self.childState=self.substates[self.idx]
    def prevState(self):
        if self.childState:
            self.childState.prevState()
    def childEndedPrev(self):
        self.idx-=1
        if self.idx==-1:
            self.notifyParentPrev()
        else:
            self.childState=self.substates[self.idx]
    def __init__(self,ts : "topState.TopState | state.State",l:list[state.State],m:Media| None = None):
        super().__init__(ts)
        if not l:
            print("Empty list not supported")
        self.substates=l
        self.idx=0
        self.childState=l[0]
        self.media=m
        self.kind="CustumState"
    def atMediaEnd(self, m:Media):
        if m.atEndIdx==-1:
            return
        self.idx=m.atEndIdx
        self.childState=self.substates[self.idx]
    def print(self):
        print(self.idx)
        return super().print()
