from dataclasses import dataclass
from talk import Talk, TalkState, readTalks
from state import State
from song import *
from songReader import readSongs

@dataclass
class DisplayWindowData:
    state : State
    songs:list [Song]
    talks:list[Talk]
    musics:list[str]
    
    def __init__(self,mainWindow):
        self.songs=readSongs("./res/songs/")
        self.talks = readTalks("./res/talks.json")
        self.musics = [] #TODO
        self.state=TalkState(mainWindow,self.talks[1])
