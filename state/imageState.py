from state.config import Config
import state.state as state
import state.topState as topState
from dataclasses import dataclass
import os

@dataclass 
class Image:
    path:str
    invertable:bool=True

class ImageState(state.State):
    image:Image
    def nextState(self):
        self.notifyParentNxt()
    def prevState(self):
        self.notifyParentPrev()
    def __init__(self,ts : "topState.TopState | state.State",i:Image):
        super().__init__(ts)
        self.image=i
        self.kind="ImageState"
    def print(self):
        print(self.image.path)
        return super().print()

def importImages(path:str,c:Config):
    res:list[Image]=[]
    for file in os.listdir(path):
        res.append(Image(path+file,not (file in c.nonInvertableImages)))
    print(c.nonInvertableImages)
    return res
