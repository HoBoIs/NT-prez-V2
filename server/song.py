from dataclasses import dataclass


@dataclass
class Song:
    titles:list[str]
    verses:list[str]
    comment: str

from songReader import readSongs
from state import State

class SongState(State):
    actual :Song =Song([],[],"")
    verseIdx: int = 0
    def __init__(self,mainWindow,song,verseIdx=0):
        self.actual=song
        self.verseIdx=verseIdx
        super().__init__(mainWindow)
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
    def render(self):
        self.mainWindow.displayVerse(self.actual.verses[self.verseIdx])
import random
from config import config

class SongListState(State):
    songs:list[Song]=[]
    SongIdx:int=0
    atEnd=False
    logos=["",""]
    def __init__(self,mainWindow):
        self.songs=readSongs(config.songDir)
        super().__init__(mainWindow)
    def nextState(self):
        if (self.childState):
            self.childState.nextState()
        else: 
            self.childState=SongState(self.mainWindow,song=self.songs[self.SongIdx])
    def prevState(self):
        if (self.childState):
            self.childState.prevState()
        else:
            s=self.songs[self.SongIdx]
            self.childState=SongState(self.mainWindow,song=s,verseIdx=len(s.verses))
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
    def render(self):
        if (self.childState):
            self.childState.render()
        else:
            if self.atEnd:
                self.mainWindow.displayImage(random.choice(self.logos))
            else:
                self.mainWindow.displayVerse("")
