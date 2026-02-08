from dataclasses import dataclass
from threading import Lock
from state.song import Song
from state.talk import Talk
import state.state as state
import state.mediainfo as mediainfo

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
    templstes : list[str] #FIXME
@dataclass
class TopState:
    data : dataContainer
    _lock:Lock =Lock()
    audioFile : None | str=None
    videoFile : None | str=None
    imageFile: None | str = None
    _opts = options()
    _m_info=mediainfo.mediaInfo()
    def __init__(self,data:dataContainer):
        self._state=state.State(self )
        self.data=data
    
