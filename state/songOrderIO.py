from state.song import Song
from state.topState import SongOrderItem, dataContainer
from state.custumState import StateMaker
from state.songState import SongState
from state.talkState import TalkState
from state.talk import Talk
from dataclasses import dataclass,asdict
from state.topState import TopState
from state.state import State
import json

def readSongOrder(path:str,dt:dataContainer):
    res:list[SongOrderItem]=[]
    songDict:dict[str,Song]={}
    for s in dt.songs.values():
        for t in s.titles: 
            songDict[t]=s
    talkDict:dict[str,Talk]={}
    for s in dt.talks.values():
        t = s.title
        talkDict[t]=s
    try:
        with open(path) as f:
            d=json.load(f)
    except:
        return res
    for data in d:
        kind=data["kind"]
        if kind=="song":
            _id=songDict[data["title"]]._id
            res.append(SongOrderItem( lambda p,i=_id: SongState(p,p.topState.data.songs[i]),data["title"],kind,_id ))
        elif kind=="talk":
            _id=talkDict[data["title"]]._id
            res.append(SongOrderItem(lambda p,i=_id: TalkState(p,p.topState.data.talks[i]),data["title"],kind,_id) )
    return res
@dataclass
class printClass:
    kind:str
    title:str
def transform(s:SongOrderItem)->printClass:
    return printClass(s.kind,s.title)
    

def writeSongOrder(path:str,l:list[SongOrderItem]):
    toPrint=[asdict(transform(t)) for t in l]
    with open(path,"w") as f:
        f.write(json.dumps(toPrint,sort_keys=True, indent=2))
