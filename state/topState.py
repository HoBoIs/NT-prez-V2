from dataclasses import dataclass
from threading import Lock
from typing import Callable
from state.imageState import Image
from state.song import Song
from state.talk import Talk
import state.state as state
import state.mediainfo as mediainfo
from state.template import Template
import state.config as conf

@dataclass
class options:
    autoPlay:bool=True
    Volume: float=0.8
    sleepLength = 3
    inversion=False

@dataclass
class dataContainer:
    songs:list[Song]
    talks:list[Talk]
    musics:list[str]
    templstes : list[Template] 
    images:list[Image]
    imagesAfterSongs:list[Image]
    imagesBeforeSongs:list[Image]
@dataclass
class Margins:
    top:   float= 0
    left:  float= 0
    bottom:float= 0
    right: float= 0
@dataclass
class TopState:
    data : dataContainer
    margins:Margins
    chg:conf.Config
    subs:list[tuple [Callable,str]]
    _lock:Lock =Lock()
    audioFile : None | str=None
    videoFile : None | str=None
    imageFile: None | str = None
    _opts = options()
    _m_info=mediainfo.mediaInfo()
    def __init__(self,data:dataContainer,c:conf.Config):
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
        for s in self.data.songs:
            for t in s.titles:
                if matchFn(t,title):
                    return s
        return None
    def findImg(self,img:str):
        for s in self.data.images:
            if s.path.endswith("/"+img):
                return s
        return Image("",True)#Just to avoid static type errors We never get here
'''
    def subsscribeChange(self,foo:Callable,name:str):
        self.subs.append((foo,name))
    def notifyAll(self,notifyer,msg):
        for f,n in self.subs:
            if n!=notifyer:
                f(msg)
                '''
