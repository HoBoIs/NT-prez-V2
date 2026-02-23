from state.state import State


class MusicListState(State):
    musics:list[str]
    idx=0
    waiting=True
    def __init__(self, tw,m:list[str]):
        self.musics=m
        super().__init__(tw)
        self.kind="MusicListState"
    def nextState(self):
        if self.topState._opts.autoPlay:
            if self.waiting:
                self.waiting=False
                self.idx+=1
                if self.idx==len(self.musics):
                    self.idx=0
                self.play()
            else:
                self.waiting=True
                self.mediaAllerts.append("SLEEP")
        return super().nextState()
    def prevState(self):
        return super().prevState()
    def pause(self): 
        self.mediaAllerts+=["PAUSE"]
    def play(self):
        self.topState.audioFile=self.musics[self.idx]
        self.mediaAllerts+=["PLAY"]
    def stop(self): 
        self.mediaAllerts+=["STOP"]
