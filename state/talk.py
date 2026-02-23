from dataclasses import dataclass,field

from state.template import Template

@dataclass
class Talk:
    title:str
    name:str
    mediaPath:str
    isMusic: bool
    thanks: tuple[Template,list[str]]
    pictures:list[str] 
    musicSong : str | None

import json
def readTalks(path:str,templates:list[Template]):
    res:list[Talk]=[]
    with open(path) as f:
        d=json.load(f)
        for data in d:
            t0=Template([],[],[])
            for t in templates:
                if data['thanks']["title"] in t.titles:
                    t0=t
            res.append( Talk (
                title=data['title'],
                name=data['name'],
                mediaPath=("./res/videos/" if data['isVideo'] else "./res/talkmusic/")+data['music'],
                isMusic=not data['isVideo'],
                pictures=data['images'],
                thanks=(t0,data["thanks"]["names"]),
                musicSong= data['TextOfMusic'] if 'TextOfMusic' in data else None
            ))
    print(templates)
    return res
