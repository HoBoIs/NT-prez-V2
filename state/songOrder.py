import enum
from state.custumState import CustumState,StateMaker
from state.image import Image
from state.imageState import ImageState
import state.topState as topState
from state.topState import MediaDescript
import state.state as state
import random
class SongOrder(CustumState):
    class status(enum.Enum):
        before=-1
        during=0
        after=1
    imageBefore:bool
    imageAfter:bool
    between:status
    def __init__(self, ts: "topState.TopState | state.State", cs: list[StateMaker], m: MediaDescript | None = None):
        super().__init__(ts, cs, m)
        self.between=self.status.during
        self.imageBefore=True
        self.imageAfter=True
    def childEndedNxt(self):
        if self.between!=self.status.during or not self.imageAfter:
            self.between=self.status.during
            super().childEndedNxt()
            self.between=self.status.after
        else:
            self.between=self.status.after
            images=self.topState.data.imagesAfterSongs
            image=random.choice(images)
            self.childState=ImageState(self,image)
    def childEndedPrev(self):
        if self.between !=self.status.during or not self.imageAfter:
            self.between=self.status.during
            super().childEndedPrev()
            self.between=self.status.before
        else:
            self.between=self.status.before
            images=self.topState.data.imagesBeforeSongs
            if images:
                image=random.choice(images)
            else:
                image=Image("",True)
            self.childState=ImageState(self,image)
    def setIndex(self,idx:int):
        self.between=self.status.during
        super().setIndex(idx)
    def nextPreview(self):
        if self.between==self.status.after and self.idx+1==len(self.constructors):
            return self.parentState.nextPreview() if self.parentState else ""
        if self.between==self.status.during:
            return "Dal utáni Logó"
        else:
            newIdx=self.idx + (1 if self.between == self.status.after else 0)
            if newIdx==len(self.constructors):
                newIdx=0
            tmp=self.constructors[newIdx](self)
            tmp.setIndex(0)
            return tmp.actPreview()
    def prevPreview(self) -> str:
        if self.between==self.status.before and self.idx==0:
            return self.parentState.prevPreview() if self.parentState else ""
        if self.between==self.status.during:
            return "Dal elötti üres"
        else:
            newIdx=self.idx - (0 if self.between == self.status.after else 1)
            if newIdx==len(self.constructors):
                newIdx=-1
            tmp=self.constructors[newIdx](self)
            tmp.setIndex(-1)
            return tmp.actPreview()
    def actPreview(self) -> str:
        if self.between==self.status.during:
            return "" #unreachable
        if self.between==self.status.after:
            return "Dal utáni Logó"
        if self.between==self.status.before:
            return "Dal elötti üres"
        return ""#unreachable
