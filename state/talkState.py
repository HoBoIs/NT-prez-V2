from dataclasses import dataclass,field
from enum import Enum
from state.state import State
from state.talk import Talk
#from state.song import Song
@dataclass
class TalkState(State):
    talk:Talk=Talk("","","",True,"",[])
    class part(Enum):
        during=0
        music=1
        thank=2
    p:part=part.during
    idx=0
    def __init__(self, ts ,t:Talk):
        self.talk=t
        self.p=self.part.during
        super().__init__(ts)
        self.kind="TalkState"
    """def showTalk(self):
        self.p=self.part.during
        self.mainWindow.displayTalk(self.talk.title,self.talk.name)"""
    def startMusic(self):
        self.p=self.part.music
        print(3,self.talk.mediaPath)
        if self.talk.isMusic:
            self.topState.audioFile=self.talk.mediaPath
            self.topState.videoFile=""
            self.mediaAllerts.append("PLAY")
        else:
            self.topState.videoFile=self.talk.mediaPath
            self.topState.audioFile=""
            self.mediaAllerts.append("PLAY")
    def showThanks(self):
        self.p=self.part.thank
        self.mediaAllerts.append("STOP")
    def nextState(self):
        self.idx+=1
        if self.p==self.part.during and self.idx>len(self.talk.pictures):
            self.idx=len(self.talk.pictures)
        if self.p==self.part.music and self.idx>len(self.talk.musicSong):
            self.idx=len(self.talk.musicSong)
    def prevState(self):
        self.idx-=1
        if self.idx<-1:
            self.idx=-1
"""
    def render(self):
        if self.p==self.part.during:
            if -1<self.idx<len(self.talk.pictures):
                self.mainWindow.displayPicture(self.talk.pictures[self.idx])
            else:
                self.mainWindow.displayTalk(self.talk.title,self.talk.name)
        elif self.p == self.part.music:
            #TODO video
            if self.talk.musicSong!=None and -1<self.idx<len(self.talk.musicSong):
                self.mainWindow.displayVerse(self.talk.musicSong[self.idx])
            else:
                self.mainWindow.displayTalk(self.talk.title,self.talk.name)
        else: #thank
            self.mainWindow.displayVerse(self.talk.thanks)
"""
            

    
