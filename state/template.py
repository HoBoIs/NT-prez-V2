from dataclasses import dataclass
import state.song as song
import os
import json


@dataclass
class Template:
    titles:list[str]
    verses:list[str]
    params:list[int]
    _id:int

def makeSongUnchecked(t:Template,l:list[list[str]]):
    return song.Song(titles=t.titles,verses=[v.format(*(l[i])) for i,v in enumerate(t.verses)],_id=-1)
def makeSongChecked(t:Template,l:list[list[str]]):
    for i in range(len(t.params)):
        if len(l)<=i:
            l+=[]
        if len(l[i])<t.params[i]:
            l[i]+=(t.params[i]-len(l[i]))*["____"]
    return song.Song(titles=t.titles,verses=[v.format(*(l[i])) for i,v in enumerate(t.verses)],_id=-1)

def readTemplate(path:str,nextID:int)->Template:
    with open(path) as f:
        data=json.load(f)
        if "lent_verses" in data:
            pass #TODO
        cnts=[s.count('{}') for s in data['sections']]
        return Template(data['titles'],data['sections'],cnts,nextID)

def readTemplates(path:str)->dict[int,Template]:
    res :dict[int,Template]={}
    was=set()
    path.strip()
    for file in os.listdir(path+"/custom"):
        file=(path+"custom/")+file
        if file.endswith(".json"):
            try:
                res[len(res)]=readTemplate(file,len(res))
                for t in res[-1].titles:
                    was.add(t)
            except Exception as e:
                print(e)
    #res+=[Song(["---SEPARATOR---"],[],"")]
    for file in os.listdir(path+"/default"):
        file=(path+"default/")+file

        if file.endswith(".json"):
            try:
                tmp=readTemplate(file,len(res))
                tmp.titles=list( filter(lambda x: not x in was ,tmp.titles))
                if len(tmp.titles)!=0:
                    res[len(res)]=tmp
            except Exception as e:
                print(e)
                print(file)
    return res
