from dataclasses import dataclass,field

from state.config import Config
from state.template import Template

@dataclass
class TalkMedia:
    path:str
    isMusic: bool
    musicSong : str | None
    autoPlay: bool

@dataclass
class Talk:
    title:str
    name:str
    media:TalkMedia
    thanks: tuple[Template,list[str]]
    pictures:list[str] 
    _id:int
    orderIDX:int

def makeFakeTalk()->Talk:
    return Talk("","",TalkMedia("",True,"",True),(Template([],[],[],-1),[]),[],-1,-1 )
import json
def readTalks(path:str,templates:list[Template],dr:str):
    res:list[Talk]=[]
    with open(path) as f:
        d=json.load(f)
        for data in d:
            t0=Template([],[],[],-1)
            for t in templates:
                if data['thanks']["title"] in t.titles:
                    t0=t
            d=data["media"]
            m=TalkMedia(
                    path=(dr)+d["path"],
                    isMusic=not d["isVideo"],
                    musicSong=d["song"],
                    autoPlay=d["autoPlay"])
            res.append( Talk (
                title=data['title'],
                name=data['name'],
                media=m,
                pictures=data['images'],
                thanks=(t0,data["thanks"]["names"]),
                _id=len(res),
                orderIDX=len(res)
            ))
    return {x._id:x for x in res}
