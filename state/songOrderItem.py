from state.talkState import TalkState
from state.songState import SongState
from state.song import Song
from state.talk import Talk
from dataclasses import dataclass
from state.custumState import StateMaker

SongOrderItemType=Song|Talk

@dataclass
class SongOrderItem:
    cnst:"StateMaker"
    title: str
    kind:str
    _id:int
    data:SongOrderItemType
    def __init__(self,data:SongOrderItemType ) -> None:
        self.data=data
        match data:
            case Song():
                self._id=data._id
                self.kind="song"
                self.title="|".join(data.titles)
                self.cnst=lambda p, i=data._id: SongState(p,p.topState.data.songs[i])
                return
            case Talk():
                self._id=data._id
                self.kind="talk"
                self.title=data.title
                self.cnst=lambda p, i=data._id: TalkState(p,p.topState.data.talks[i])
                return
            case _:
                assert_never(data)
