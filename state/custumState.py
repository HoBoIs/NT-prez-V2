from typing import Callable
import state.state as state
import state.topState as topState
from dataclasses import dataclass
from state.topState import MediaDescript


class CustumState(state.State):
    substates:list[state.State]
    idx:int
    media:MediaDescript | None
    def getMedia(self):
        if self.childState:
            if res:= self.childState.getMedia():
                return res
        return self.media
    def nextState(self):
        if self.childState:
            self.childState.nextState()
    def childEndedNxt(self):
        if self.idx+1==len(self.substates):
            self.notifyParentNxt()
        else:
            self.idx+=1
            self.childState=self.substates[self.idx]
    def prevState(self):
        if self.childState:
            self.childState.prevState()
    def childEndedPrev(self):
        if self.idx==0:
            self.notifyParentPrev()
        else:
            self.idx-=1
            self.childState=self.substates[self.idx]
    def __init__(self,ts : "topState.TopState | state.State",l:list[state.State],m:MediaDescript| None = None):
        super().__init__(ts)
        if not l:
            print("Empty list not supported")
        self.substates=l
        self.idx=0
        self.childState=l[0]
        self.media=m
        self.kind="CustumState"
    """def atMediaEnd(self, m:Media):
        if m.atEndIdx==-1:
            return
        self.idx=m.atEndIdx
        self.childState=self.substates[self.idx]"""
    def destruct(self):
        for s in self.substates:
            s.destruct()
        self.substates=[]
        return super().destruct()
    def print(self):
        print(self.idx)
        return super().print()
