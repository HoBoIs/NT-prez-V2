from dataclasses import dataclass,field
from enum import Enum
from state import topState
from state.songState import SongState
from state.state import State
from state.talk import Talk
from state.template import Template, makeSongChecked
import state.titleState as tlState
import state.custumState as custumState
import state.imageState as imgState
#from state.song import Song

class TalkState(custumState.CustumState):
    talk:Talk
    thxIdx:int
    def __init__(self, ts:topState.TopState | State ,t:Talk):
        self.talk=t
        self.shouldPlay=False
        if isinstance(ts,topState.TopState):
            self.topState=ts
        else:
            self.topState=ts.topState
        l:list[State]=[tlState.TitleState(self,tlState.Title(t.title,t.name))]
        if not isinstance(ts,topState.TopState):
            t0=ts.topState
        else: 
            t0=ts
        if t.pictures:
            l+=[imgState.ImageState(self,t0.findImg(i)) for i in t.pictures]
            l+=[tlState.TitleState(self,tlState.Title(t.title,t.name))]
        if s:=t0.findSong(t.musicSong):
            l+=[SongState(self,s)]
        m=custumState.MediaDescript(t.isMusic,t.mediaPath,self.toThanks,self)
        self.thxIdx=len(l)
        l+=[SongState(self,makeSongChecked(t.thanks[0],[t.thanks[1]]))]
        if len(l)==self.thxIdx:
            self.thxIdx=-1
        super().__init__(ts,l,m)
        print(self.talk)
        self.kind="TalkState"
    def toThanks(self):
        if self.thxIdx==-1:
            return
        self.idx=self.thxIdx
        self.childState=self.substates[self.idx]
    def print(self):
        return super().print()


