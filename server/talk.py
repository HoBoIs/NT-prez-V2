from dataclasses import dataclass,field
from enum import Enum
#from mainWindow import MainWindow
from state import State
from song import Song
@dataclass
class Talk:
    title:str
    name:str
    mediaPath:str
    isMusic: bool
    thanks: str
    pictures:list[str] 
    musicSong : list[str] = field(default_factory=lambda:[])

class TalkState(State):
    talk:Talk
    class part(Enum):
        during=0
        music=1
        thank=2
    p:part
    idx=0
    def __init__(self, mainWindow : "MainWindow",t:Talk):
        self.talk=t
        self.p=self.part.during
        super().__init__(mainWindow)
    """def showTalk(self):
        self.p=self.part.during
        self.mainWindow.displayTalk(self.talk.title,self.talk.name)"""
    def startMusic(self):
        self.p=self.part.music
        print(3,self.talk.mediaPath)
        if self.talk.isMusic:
            self.mainWindow.playMusic(self.talk.mediaPath,self.showThanks)
        else:
            self.mainWindow.playVideo(self.talk.mediaPath,self.showThanks)
    def showThanks(self):
        self.p=self.part.thank
        self.mainWindow.stop()
        self.mainWindow.displayVerse(self.talk.thanks)
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

            

    
import json
def readTalks(path:str):
    res:list[Talk]=[]
    with open(path) as f:
        d=json.load(f)
        for data in d:
            res.append( Talk (
                title=data['title'],
                name=data['name'],
                mediaPath=("./res/songs/" if data['isVideo'] else "./res/talkmusic/")+data['music'],
                isMusic=not data['isVideo'],
                pictures=data['images'],
                thanks="TODO"
            ))
    return res
