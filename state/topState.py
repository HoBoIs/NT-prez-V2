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
class dataContainer:
    songs:dict[int,Song]
    talks:dict[int,Talk]
    musics:list[str]
    templstes : dict[int,Template] 
    images:list[Image]
    imagesAfterSongs:list[Image]
    imagesBeforeSongs:list[Image]
    songOrder:list[ "SongOrderItem"]

@dataclass
class Margins:
    top:   float= 0
    left:  float= 0
    bottom:float= 0
    right: float= 0
@dataclass
class TopState:
    port:int
    ip:str
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
        self.ip=""
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

from state.songOrderItem import SongOrderItem
