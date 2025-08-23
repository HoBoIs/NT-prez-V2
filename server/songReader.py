from song import Song
import os
import json

def readSong(path:str)->Song:
    with open(path) as f:
        data=json.load(f)
        c=""
        if "comment" in data:
            c=data["comment"]
        if "lent_verses" in data:
            pass #TODO
        return Song(data['titles'],data['verses'],c)

def readSongs(path:str)->list[Song]:
    res :list[Song]=[]
    for file in os.listdir(path+"/default"):
        if file.endswith(".json"):
            try:
                res+=[readSong(file)]
            except Exception as e:
                print(e)
                pass
    res+=[Song(["---SEPARATOR---"],[],"")]
    for file in os.listdir(path+"/custom"):
        if file.endswith(".json"):
            try:
                res+=[readSong(file)]
            except Exception as e:
                print(e)
    return res
