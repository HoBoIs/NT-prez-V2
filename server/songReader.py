from song import Song
import os
import json

def readSong(path:str)->Song:
    with open(path) as f:
        data=json.load(f)
        c=""
        if "comment" in data:
            c=data["comment"]
        return Song(data['titles'],data['verses'],c)

def readSongs(path:str)->list[Song]:
    res=[]
    for file in os.listdir(path):
        if file.endswith(".json"):
            try:
                res+=[readSong(file)]
            except:
                pass
    return res
