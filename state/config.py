from dataclasses import dataclass,asdict
import json
import os
import shutil

@dataclass
class Config:
  maxSongFont : float
  maxTalkFont : float
  sleepLength : float
  port : int
  imagesAfterSong : list[str]
  imagesBeforeSong : list[str]
  musicDir : str
  imageDir : str
  songDir  : str
  videoDir : str
  talkMusicDir : str
  origDir : str
  nonInvertableImages:list[str]
  templateDir : str
  server : bool

def readConfig():
    origDir= os.path.dirname(__file__)+"/../"
    if not os.path.isfile(origDir+"res/config.json"):
        shutil.copy(origDir+"res/default_config.json",origDir+"res/config.json")
    with open(origDir+"res/config.json") as f:
        data=json.load(f)
        return Config(
          origDir=origDir,
          maxSongFont=data["maxSongFont"],
          maxTalkFont=data["maxTalkFont"],
          sleepLength=data["sleepLength"],
          port=data["port"],
          imagesAfterSong=data["imagesAfterSong"],
          imagesBeforeSong=data["imagesBeforeSong"],
          musicDir=origDir+data["musicDir"],
          imageDir=origDir+data["imageDir"],
          templateDir=origDir+data["templateDir"],
          songDir=origDir+data["songDir"],
          videoDir=origDir+data["videoDir"],
          talkMusicDir=origDir+data["talkMusicDir"],
          server=data["server"],
          nonInvertableImages=data["nonInvertableImages"]
          )
def stripOrig(s1:str,o:str):
    return s1[len(o):]
def writeConfig(c:Config):
    origDir=c.origDir 
    with open(origDir+"res/config.json","w") as f:
        dr:dict=asdict(c)
        for k in dr:
            if k.endswith("Dir"): dr[k]=stripOrig(dr[k],origDir)
        dr.pop("origDir")
        f.write(json.dumps(dr,sort_keys=True, indent=2))

