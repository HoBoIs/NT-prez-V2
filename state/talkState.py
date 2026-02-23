from dataclasses import dataclass,field
from enum import Enum
from state import topState
from state.song import SongState
from state.state import State
from state.talk import Talk
from state.template import Template, makeSongChecked
import state.titleState as tlState
import state.custumState as custumState
import state.imageState as imgState
#from state.song import Song

class TalkState(custumState.CustumState):
    talk:Talk
    def __init__(self, ts:topState.TopState | State ,t:Talk):
        self.talk=t
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
        m=custumState.Media(t.isMusic,len(l),t.mediaPath,self)
        l+=[SongState(self,makeSongChecked(t.thanks[0],[t.thanks[1]]))]
        super().__init__(ts,l,m)
        print(self.talk)
        self.kind="TalkState"
    def print(self):
        return super().print()


