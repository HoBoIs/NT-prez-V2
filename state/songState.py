from state.song import Song
from state import topState
from state.imageState import ImageState
from state.image import Image
import state.state as state

class SongState(state.State):
    actual :Song =Song([],[])
    verseIdx: int = 0
    def __init__(self,tw,song,verseIdx=0):
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

from state.config import Config

class SongListState(state.State):
    songs:list[Song]
    SongIdx:int=0
    atEnd=False
    inSong=True
    def __init__(self,ts,songs,idx=0,verseIdx=0):
        super().__init__(ts)
        self.inSong=True
        self.songs=songs
        self.SongIdx=idx
        self.childState=SongState(self,song=self.songs[idx],verseIdx=verseIdx)
        self.atEnd=False
        self.kind="SongListState"
    def nextState(self):
        if (self.childState):
            self.childState.nextState()
        else: 
            self.childState=SongState(self,song=self.songs[self.SongIdx])
    def prevState(self):
        if (self.childState):
            self.childState.prevState()
        else:
            self.SongIdx-=1
            if self.SongIdx==-1:
                self.SongIdx=len(self.songs)-1
            s=self.songs[self.SongIdx]
            self.childState=SongState(self,song=s,verseIdx=len(s.verses)-1)
    def childEndedNxt(self):
        self.inSong=not self.inSong
        if not self.inSong:
            image=Image("")
            if l:=self.topState.data.imagesAfterSongs:
                image=l[0] #TODO choose random
            self.childState=ImageState(self,image)
        else:
            self.SongIdx+=1
            if self.SongIdx==len(self.songs):
                self.SongIdx=0
            self.childState=SongState(self,song=self.songs[self.SongIdx])


    def childEndedPrev(self):
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
    def print(self):
        print(self.SongIdx,self.songs[self.SongIdx].titles)
        return super().print()

    """def render(self):
        if (self.childState):
            self.childState.render()
        else:
            if self.atEnd:
                self.mainWindow.displayImage(random.choice(self.logos))
            else:
                self.mainWindow.displayVerse("")
                """
