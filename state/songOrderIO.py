from state.song import Song
from state.topState import dataContainer
from state.custumState import StateMaker
from state.songState import SongState
from state.talkState import TalkState
from state.talk import Talk
from dataclasses import dataclass,asdict
from state.topState import TopState
from state.state import State
import json
from state.songOrderItem import SongOrderItem

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
        print("ERROR LOADING")
        return res
    for data in d:
        kind=data["kind"]
        if kind=="song":
            s=songDict[data["title"]]
            res.append(SongOrderItem(s))
        elif kind=="talk":
            t=talkDict[data["title"]]
            res.append(SongOrderItem(t))
    return res
@dataclass
class printClass:
    kind:str
    title:str
def transform(s:SongOrderItem)->printClass:
    return printClass(s.kind,s.title.split("|")[0])
    

def writeSongOrder(path:str,l:list[SongOrderItem]):
    toPrint=[asdict(transform(t)) for t in l]
    with open(path,"w") as f:
        f.write(json.dumps(toPrint,sort_keys=True, indent=2))
