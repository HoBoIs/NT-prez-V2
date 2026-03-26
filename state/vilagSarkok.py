from dataclasses import dataclass
from state.config import Config
from state.image import Image
from state.imageState import ImageState
from state.songState import SongState
from state.state import State
from state.song import Song
from state.topState import TopState
@dataclass
class City:
    name:str
    x:float
    y:float

class VilagSarkok(State):
    cities:list[City]
    s:SongState
    img:ImageState
    idx:int
    def __init__(self, ts: TopState | State,c:Config,cities:list[str] ):
        super().__init__(ts)
        with open(c.origDir+"/res/varosok.txt","r") as f:
            lines=f.readlines()
        dct={l.split(',')[0]:(l.split(',')[1],l.split(',')[2]) for l in lines}
        self.cities=[City(city,float(dct[city][0]),float(dct[city][1])) for city in cities if city in dct]
        for city in cities:
            if city not in dct:
                print(city,"is not in the database, ignoring it!") #TODO show error on popup
        s=self.topState.findSong("A fény, ami bennem ég")
        i=self.topState.findImg("Hungary_map_blank.svg")
        assert i and s
        self.s=SongState(self, s)
        self.childState=self.s
        self.img=ImageState(self,i)
        self.idx=0
    def childEndedNxt(self):
        if self.childState==self.s:
            self.childState=self.img
        else:
            if self.idx+1<len(self.cities):
                self.idx+=1
            else:
                self.notifyParentNxt()

    def childEndedPrev(self):
        if self.childState==self.s:
            self.notifyParentPrev()
        else:
            if self.idx>0:
                self.idx-=1
            else:
                self.childState=self.s
    def setIndex(self, idx: int):
        if idx==-1:
            idx+=len(self.cities)
        else:
            idx+=1
        self.idx=idx
        if self.idx==0:
            self.childState=self.s
        else:
            self.childState=self.img
    def nextState(self):
        if self.childState:
            self.childState.nextState()
    def prevState(self):
        if self.childState:
            self.childState.prevState()
    def getCities(self):
        return self.cities[:self.idx+1]
    def nextPreview(self)->str:
        if self.childState==self.s:
            return self.cities[0].name
        if self.idx+1!=len(self.cities):
            return self.cities[self.idx+1].name
        if self.parentState:
            return self.parentState.nextPreview()
        return 'N/A'
    def prevPreview(self)->str:
        if self.childState==self.s:
            if self.parentState:
                return self.parentState.prevPreview()
            return 'N/A'
        if self.idx!=0:
            return self.cities[self.idx-1].name
        else:
            return self.s.actual.verses[-1].split('\n')[0]
    def actPreview(self)->str:
        return "N/A"
