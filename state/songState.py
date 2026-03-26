from state.song import Song
from state import topState
from state.imageState import ImageState
from state.image import Image
import state.state as state

class SongState(state.State):
    actual :Song
    verseIdx: int = 0
    def __init__(self,tw:"state.State | topState.TopState" ,song:Song,verseIdx=0):
        self.actual=song
        self.verseIdx=verseIdx
        super().__init__(tw)
        self.kind="SongState"
    def nextState(self):
        if (self.verseIdx+1 < len(self.actual.verses)):
            self.verseIdx+=1
        elif self:
            self.notifyParentNxt()
    def prevState(self):
        if self.verseIdx > 0: 
            self.verseIdx-=1
        elif self:
            self.notifyParentPrev()
    def print(self):
        print(self.verseIdx,self.actual.verses[self.verseIdx])
        return super().print()
    def setIndex(self, idx):
        if idx==-1:
            idx+=len(self.actual.verses)
        self.verseIdx=idx
    def nextPreview(self) -> str:
        if self.verseIdx+1 == len(self.actual.verses):
            if self.parentState:
                return self.parentState.nextPreview()
            return ""
        else:
            return self.actual.verses[self.verseIdx+1].split("\n")[0]
    def prevPreview(self) -> str:
        if self.verseIdx == 0:
            if self.parentState:
                return self.parentState.prevPreview()
            return ""
        else:
            return self.actual.verses[self.verseIdx-1].split("\n")[0]
    def actPreview(self) -> str:
        return self.actual.verses[self.verseIdx].split("\n")[0]
    def getIdxsForFL(self) -> list[int]:
        return [self.verseIdx]

"""
SongListState is no longer needed.
Functionality was merged into SongOrderState

class SongListState(state.State):
    songs:list[Song]
    SongIdx:int=0
    atEnd=False
    inSong=True
    def __init__(self,ts:"state.State | topState.TopState",songs:list[Song],idx=0,verseIdx=0):
        super().__init__(ts)
        self.inSong=True
        self.songs=songs
        self.SongIdx=idx
        self.childState=SongState(self,song=self.songs[idx],verseIdx=verseIdx)
        self.atEnd=False
        self.kind="SongListState"
    def nextState(self):
        self.atEnd=False
        if (self.childState):
            self.childState.nextState()
        else: 
            self.childState=SongState(self,song=self.songs[self.SongIdx])
    def prevState(self):
        self.atEnd=False
        if (self.childState):
            self.childState.prevState()
        else:
            self.SongIdx-=1
            if self.SongIdx==-1:
                self.SongIdx=len(self.songs)-1
            s=self.songs[self.SongIdx]
            self.childState=SongState(self,song=s,verseIdx=len(s.verses)-1)
    def childEndedNxt(self):
        self.atEnd=False
        self.inSong=not self.inSong
        if not self.inSong:
            image=Image("")
            if l:=self.topState.data.imagesAfterSongs:
                image=l[0] #TODO choose random
            self.childState=ImageState(self,image)
            self.atEnd=True
        else:
            self.SongIdx+=1
            if self.SongIdx==len(self.songs):
                self.SongIdx=0
            self.childState=SongState(self,song=self.songs[self.SongIdx])


    def childEndedPrev(self):
        self.atEnd=False
        self.inSong=not self.inSong
        if not self.inSong:
            image=Image("")
            if l:=self.topState.data.imagesBeforeSongs:
                image=l[0] #TODO choose random
            self.childState=ImageState(self,image)
        else:
            self.SongIdx-=1
            if self.SongIdx==-1:
                self.SongIdx=len(self.songs)-1
            s=self.songs[self.SongIdx]
            self.childState=SongState(self,song=s,verseIdx=len(s.verses)-1)
        #self.childState=None
        #self.atEnd=False
    def setIndex(self, idx:int):
        if idx==-1:
            idx+=len(self.songs)
        self.SongIdx=idx
        self.childState=SongState(self,song=self.songs[self.SongIdx])
    def print(self):
        print(self.SongIdx,self.songs[self.SongIdx].titles)
        return super().print()
    def nextPreview(self):
        if self.inSong:
            return "Dal utáni Logó"
        else:
            newIdx=self.SongIdx + (1 if self.atEnd else 0)
            if newIdx==len(self.songs):
                return self.songs[0].verses[0].split('\n')[0]
            return self.songs[newIdx].verses[0].split('\n')[0]
    def prevPreview(self) -> str:
        if self.inSong:
            return "Dal elötti üres"
        else:
            newIdx=self.SongIdx - (0 if self.atEnd else 1)
            if newIdx==len(self.songs):
                return self.songs[0].verses[-1].split('\n')[0]
            return self.songs[newIdx].verses[-1].split('\n')[0]
    def actPreview(self) -> str:
        if self.inSong:
            return "N/A"#unreachable
        else:
            if self.atEnd:
                return "Dal utáni Logó"
            return "Dal elötti üres"
"""
