from dataclasses import dataclass


@dataclass
class Song:
    titles:list[str]
    verses:list[str]
    comment: str

#from server.songReader import readSongs
import server.state as state

class SongState(state.State):
    actual :Song =Song([],[],"")
    verseIdx: int = 0
    def __init__(self,tw,song,verseIdx=0):
        self.actual=song
        self.verseIdx=verseIdx
        super().__init__(tw)
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
import random
from server.config import config

class SongListState(state.State):
    songs:list[Song]=[]
    SongIdx:int=0
    atEnd=False
    logos=["",""]
    #def __init__(self):
        #self.songs=readSongs(config.songDir)
    def nextState(self):
        if (self.childState):
            self.childState.nextState()
        else: 
            self.childState=SongState(self.topState,song=self.songs[self.SongIdx])
    def prevState(self):
        if (self.childState):
            self.childState.prevState()
        else:
            s=self.songs[self.SongIdx]
            self.childState=SongState(self.topState,song=s,verseIdx=len(s.verses))
    def childEndedNxt(self):
        self.SongIdx+=1
        self.childState=None
        self.atEnd=True
        if self.SongIdx==len(self.songs):
            self.SongIdx=0

    def childEndedPrev(self):
        self.SongIdx-=1
        self.childState=None
        self.atEnd=False
        if self.SongIdx==-1:
            self.SongIdx=len(self.songs)-1
    """def render(self):
        if (self.childState):
            self.childState.render()
        else:
            if self.atEnd:
                self.mainWindow.displayImage(random.choice(self.logos))
            else:
                self.mainWindow.displayVerse("")
                """
