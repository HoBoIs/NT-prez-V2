from typing import Callable, Concatenate
from state.song import Song
from state.songState import SongState
import state.state as state
import state.topState as topState
from dataclasses import dataclass
from state.topState import MediaDescript
from typing import Callable, Generic, ParamSpec, TypeVar,Unpack,TypeVarTuple
"""
P = ParamSpec("P")
Ts = TypeVarTuple("Ts")
@dataclass
class CallableWithArgs(Generic[Unpack[Ts]]):
    fun:Callable[[state.State,Unpack[Ts]],state.State]
    params:tuple[Unpack[Ts]]
    def __call__(self, p:state.State):
        return self.fun(p,*self.params)
'''
def makeCallable(
        fun:Callable[Concatenate[state.State ,P],state.State],
        *args:P.args, 
        **kwargs: P.kwargs) -> CallableWithArgs:
    return CallableWithArgs(fun=fun,params=args) 
'''
def makeSongState(parent:state.State,songId:int):
    return SongState(parent,parent.topState.getSong(songId))

def makeSongStateMaker(songId:int)->CallableWithArgs:
    return CallableWithArgs(makeSongState,(songId,))
"""

T0 = TypeVar("T0")
P = ParamSpec("P")
R = TypeVar("R")
def CXXLambda(fun:Callable[Concatenate[T0, P],R],*args:P.args,**kwargs:P.kwargs)->Callable[[T0],R]:
    def wrapper(p: T0) -> R:
        return fun(p, *args, **kwargs)
    return wrapper

StateMaker = Callable[[state.State], state.State]

class CustumState(state.State):
    #substates:list[state.State]
    constructors:list[StateMaker]
    idx:int
    media:MediaDescript | None
    def getMedia(self):
        if self.childState:
            if res:= self.childState.getMedia():
                return res
        return self.media
    def nextState(self):
        if self.childState:
            self.childState.nextState()
    def childEndedNxt(self):
        if self.idx+1==len(self.constructors):
            self.notifyParentNxt()
        else:
            self.idx+=1
            now=self.constructors[self.idx]
            self.childState=now(self)
            if isinstance(self.childState,SongState) and self.childState.actual.verses==[]:
                self.childEndedNxt()
    def prevState(self):
        if self.childState:
            self.childState.prevState()
    def childEndedPrev(self):
        if self.idx==0:
            self.notifyParentPrev()
        else:
            self.idx-=1
            now=self.constructors[self.idx]
            self.childState=now(self)
            if isinstance(self.childState,SongState) and self.childState.actual.verses==[]:
                self.childEndedPrev()
            else:
                self.childState.setIndex(-1)
    def __init__(self,ts : "topState.TopState | state.State",cs:list[StateMaker],m:MediaDescript| None = None):
        super().__init__(ts)
        if not cs:
            print("Empty list not supported")
            raise OverflowError
        self.childState=cs[0](self)
        self.constructors=cs
        self.idx=0
        self.media=m
        self.kind="CustumState"
    def print(self):
        print(self.idx)
        return super().print()
    def setIndex(self, idx: int):
        if idx==-1:
            idx+=len(self.constructors)
        self.idx=idx
        self.childState=self.constructors[idx](self)

