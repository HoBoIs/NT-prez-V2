from state.custumState import CustumState,StateMaker
from state.imageState import ImageState
import state.topState as topState
from state.topState import MediaDescript
import state.state as state
import random

class SongOrder(CustumState):
    imageBefore:bool
    imageAfter:bool
    between:bool
    def __init__(self, ts: "topState.TopState | state.State", cs: list[StateMaker], m: MediaDescript | None = None):
        super().__init__(ts, cs, m)
        self.between=False
        self.imageBefore=True
        self.imageAfter=True
    def childEndedNxt(self):
        if self.between or not self.imageAfter:
            self.between=False
            super().childEndedNxt()
        else:
            self.between=True
            images=self.topState.data.imagesAfterSongs
            image=random.choice(images)
            self.childState=ImageState(self,image)
    def childEndedPrev(self):
        if self.between or not self.imageAfter:
            self.between=False
            super().childEndedPrev()
        else:
            self.between=True
            images=self.topState.data.imagesBeforeSongs
            image=random.choice(images)
            self.childState=ImageState(self,image)
