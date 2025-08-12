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

def readConfig():
    if not os.path.isfile("./res/config.json"):
        shutil.copy("./res/default_config.json","./res/config.json")
    with open("./res/config.json") as f:
        data=json.load(f)
        return Config(
          maxSongFont=data["maxSongFont"],
          maxTalkFont=data["maxTalkFont"],
          sleepLength=data["sleepLength"],
          port=data["port"],
          logo_images=data["logo_images"],
          musicDir=data["musicDir"],
          imageDir=data["imageDir"],
          songDir=data["songDir"],
          videoDir=data["videoDir"],
          talkMusicDir=data["talkMusicDir"])
config=readConfig()
