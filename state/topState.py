from dataclasses import dataclass
from threading import Lock
from typing import Callable
from display.mediaType import getLength
from state.image import Image
from state.song import Song
from state.songState import SongState
from state.talk import Talk
import state.state as state
from state.template import Template
import state.config as conf
import typing

if typing.TYPE_CHECKING:
    from state.custumState import CustumState

@dataclass
class MediaDescript:
    isMusic:bool
    path:str
    adEnfFun:Callable= lambda : 0
    parent:"CustumState | None"=None

@dataclass
class options:
    autoPlay:bool=True
    Volume: float=80
    sleepLength = 3
    inversion=False

@dataclass
class MediaInfo:
    descript:MediaDescript
    status:str
    length:float
    age:float
    infoDate:float

@dataclass
class SongOrderItem:
    cnst:"StateMaker"
    title: str
    kind:str
    _id:int

@dataclass
class dataContainer:
    songs:dict[int,Song]
    talks:dict[int,Talk]
    musics:list[str]
    templstes : dict[int,Template] 
    images:list[Image]
    imagesAfterSongs:list[Image]
    imagesBeforeSongs:list[Image]
    songOrder:list[ SongOrderItem]

@dataclass
class Margins:
    top:   float= 0
    left:  float= 0
    bottom:float= 0
    right: float= 0
@dataclass
class TopState:
    port:int
    data : dataContainer
    margins:Margins
    cfg:conf.Config
    subs:list[tuple [Callable,str]]
    mediaCache:dict[str,MediaInfo]
    _lock:Lock =Lock()
    media:MediaInfo | None=None
    _opts = options()
    def getSong(self,i:int):
        return self.data.songs[i]
    def getTalk(self,i:int):
        return self.data.talks[i]
    def getTemplate(self,i:int):
        return self.data.templstes[i]
    def __init__(self,data:dataContainer,c:conf.Config):
        self.port=8000
        self.mediaCache={}
        self._state=state.State(self )
        self.data=data
        self.margins=Margins()
        self.subs=[]
        self.cfg=c
    def getBonnomState(self):
        res=self._state
        #if isinstance()
        while isinstance(res.childState,state.State):
            res=res.childState
        return res
    def findSong(self,title:str| None,matchFn:Callable[[str,str],bool]=lambda x,y: x==y):
        if title==None:
            return None
        for s in self.data.songs.values():
            for t in s.titles:
                if matchFn(t,title):
                    return s
        return None
    def findImg(self,img:str):
        for s in self.data.images:
            if s.path.endswith("/"+img):
                return s
        return Image("",True)#Just to avoid static type errors We never get here
    def getMedia(self):
        res=None
        for s in self._state.getChain():
          if m:=s.getMedia():
              res=m
        if not res:
            return None
        if res.path in self.mediaCache:
            return self.mediaCache[res.path]
        else:
            return MediaInfo(res,"STOPPED",getLength(res.path),0,0)
'''
    def subsscribeChange(self,foo:Callable,name:str):
        self.subs.append((foo,name))
    def notifyAll(self,notifyer,msg):
        for f,n in self.subs:
            if n!=notifyer:
                f(msg)
                '''
from state.talkState import TalkState
from state.custumState import StateMaker
def makeConstructor(f:Song|Talk)->StateMaker:#todo for everithing we want at songorder
    if type(f)==Song:
        return lambda p, i=f._id: SongState(p,p.topState.data.songs[i])
    elif type(f)==Talk:
        return lambda p, i=f._id: TalkState(p,p.topState.data.talks[i])
    #unreachable
    raise NotImplementedError
def getKindName(f:Song|Talk):
    if type(f)==Song:
        return "song"
    elif type(f)==Talk:
        return "talk"
    #unreachable
    raise NotImplementedError
def getTitle(f:Song|Talk):
    if type(f)==Song:
        return f.titles[0]
    elif type(f)==Talk:
        return f.title
    #unreachable
    raise NotImplementedError

    
