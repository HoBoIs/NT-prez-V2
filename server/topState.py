from dataclasses import dataclass
from threading import Lock
from server.song import Song
from server.talk import Talk
import server.state as state
import server.mediainfo as mediainfo

@dataclass
class options:
    autoPlay:bool=True
    Volume: float=0.8
    sleepLength = 3

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
    
