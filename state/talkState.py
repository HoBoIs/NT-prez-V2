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
from typing import Callable
from state.image import Image
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
        cons:list[custumState.StateMaker]=[]
        def makeTS(_id:int):
            def foo(p:State):
                tmp=p.topState.getTalk(_id)
                return tlState.TitleState(p, tlState.Title(tmp.title,tmp.name))
            return foo
        cons.append(makeTS(t._id))
        if not isinstance(ts,topState.TopState):
            t0=ts.topState
        else: 
            t0=ts
        if t.pictures:
            cons+=[lambda x, img=i: imgState.ImageState(x,x.findImg(img)) for i in t.pictures]
            cons.append(makeTS(t._id))
        tmp=t.media
        if s:=t0.findSong(t.media.musicSong):
            cons.append(lambda x: SongState(x,x.topState.getSong(s._id)) )
        m=custumState.MediaDescript(tmp.isMusic,tmp.path,self.toThanks if tmp.autoPlay else lambda :0,self)
        self.thxIdx=len(cons)
        def makeThx(_id:int):
            def foo(p:State):
                tmp=p.topState.getTalk(_id)
                return  SongState(p, makeSongChecked(tmp.thanks[0],[tmp.thanks[1]]))
            return foo
        cons.append(makeThx(t._id))
        super().__init__(ts,cons,m)
        print(self.talk)
        self.kind="TalkState"
    def toThanks(self):
        tmp=self.constructors[self.thxIdx](self)
        if isinstance(tmp,SongState) and tmp.actual.verses==[]:
            return
        self.idx=self.thxIdx
        self.childState=tmp
    def print(self):
        return super().print()
    def nextPreview(self) -> str:
        toFind=self.idx+1
        if toFind>=len(self.constructors): 
            if not self.parentState:
                return ""
            return self.parentState.nextPreview()
        return self.findPreview(toFind)
    def prevPreview(self) -> str:
        toFind=self.idx-1
        if toFind==-1:
            if not self.parentState:
                return ""
            return self.parentState.prevPreview()
        return self.findPreview(toFind)
    def findPreview(self,idx:int)->str:
        if idx==0:
            return self.talk.title
        if idx<=len(self.talk.pictures):
            return self.talk.pictures[idx-1]
        if idx>1 and idx==len(self.talk.pictures)+1:
            return self.talk.title
        if idx==self.thxIdx:
            return self.talk.thanks[0].titles[0]+" "+",".join(self.talk.thanks[1]) if self.talk.thanks[0].titles else ""
        return ""
    def actPreview(self) -> str:
        return self.findPreview(self.idx)
    def nextState(self):
        super().nextState()
    def findImg(self,img:str)->Image :
        ls=self.topState.data.images
        for i in ls:
            if i.path.endswith("/"+img):
                return i
        return Image("")
    def getIdxsForFL(self) -> list[int]:
        if self.thxIdx==-1:
            return [self.idx]
        if self.idx < self.thxIdx:
            return [self.idx]
        return [self.idx] #TODO több versszakos köszönjükre felkészülni
    #TODO énekszövegre felkészülni



