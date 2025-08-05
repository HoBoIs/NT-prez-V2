from state import State


class MusicListState(State):
    musics:list[str]
    idx=0
    autoplay=True
    sleepLength=12
    waiting=True
    def __init__(self, mainWindow,m:list[str]):
        self.musics=m
        super().__init__(mainWindow)
    def nextState(self):
        if self.autoplay:
            if self.waiting:
                self.idx+=1
                if self.idx==len(self.musics):
                    self.idx=0
                self.mainWindow.playMusic(self.musics[self.idx],self.nextState())
            else:
                self.mainWindow.delayed(self.sleepLength,self.nextState())
        return super().nextState()
    def prevState(self):
        return super().prevState()
    def pause(self): 
        self.mainWindow.pause()
    def play(self,a): 
        pass
    def stop(self): 
        pass
    def render(self):
        return super().render()
