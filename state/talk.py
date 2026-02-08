from dataclasses import dataclass,field

@dataclass
class Talk:
    title:str
    name:str
    mediaPath:str
    isMusic: bool
    thanks: str
    pictures:list[str] 
    musicSong : list[str] = field(default_factory=lambda:[])

import json
def readTalks(path:str):
    res:list[Talk]=[]
    with open(path) as f:
        d=json.load(f)
        for data in d:
            res.append( Talk (
                title=data['title'],
                name=data['name'],
                mediaPath=("./res/videos/" if data['isVideo'] else "./res/talkmusic/")+data['music'],
                isMusic=not data['isVideo'],
                pictures=data['images'],
                thanks="TODO"
            ))
    return res
