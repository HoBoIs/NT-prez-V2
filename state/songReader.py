from state.song import Song
import os
import json

def readSong(path:str,nextID:int)->Song:
    with open(path) as f:
        data=json.load(f)
        if "lent_verses" in data:
            pass #TODO
        return Song(data['titles'],data['sections'],nextID)

def readSongs(path:str)->dict[int,Song]:
    res :list[Song]=[]
    was=set()
    for file in os.listdir(path+"/custom"):
        file=(path+"custom/")+file
        if file.endswith(".json"):
            try:
                res+=[readSong(file,len(res))]
                for t in res[-1].titles:
                    was.add(t)
            except Exception as e:
                print(e)
    #res+=[Song(["---SEPARATOR---"],[],"")]
    for file in os.listdir(path+"/default"):
        file=(path+"default/")+file

        if file.endswith(".json"):
            try:
                tmp=readSong(file,len(res))
                tmp.titles=list( filter(lambda x: not x in was ,tmp.titles))
                if len(tmp.titles)!=0:
                    res+=[tmp]
            except Exception as e:
                print(e)
                print(file)
    res.sort(key=lambda x: x.titles[0])
    return {x._id:x for x in res}
