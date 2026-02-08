from dataclasses import dataclass
import json
import os
import shutil

@dataclass
class Config:
  maxSongFont : float
  maxTalkFont : float
  sleepLength : float
  port : int
  logo_images : list[str]
  musicDir : str
  imageDir : str
  songDir  : str
  videoDir : str
  talkMusicDir : str
  origDir : str

def readConfig():
    origDir= os.path.dirname(__file__)+"/"
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
          logo_images=data["logo_images"],
          musicDir=origDir+data["musicDir"],
          imageDir=origDir+data["imageDir"],
          songDir=origDir+data["songDir"],
          videoDir=origDir+data["videoDir"],
          talkMusicDir=origDir+data["talkMusicDir"])
config=readConfig()
