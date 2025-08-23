from dataclasses import dataclass
from talk import Talk, TalkState, readTalks
from state import State
from song import *
from songReader import readSongs
import os
import shutil
from config import config

@dataclass
class DisplayWindowData:
    state : State
    songs:list [Song]
    talks:list[Talk]
    musics:list[str]
    
    def __init__(self,mainWindow):
        self.songs=readSongs(config.songDir)
        if not os.path.isfile(config.origDir+"res/talks.json"):
            shutil.copy(config.origDir+"res/default_talks.json","res/talks.json")
        self.talks = readTalks(config.origDir+"res/talks.json")
        self.musics = [] #TODO
        self.state=TalkState(mainWindow,self.talks[1])
