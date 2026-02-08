from state.songReader import readSongs
from state.topState import TopState, dataContainer
import state.talk as talk
songs=readSongs("./state/res/songs/")
talks=talk.readTalks("./state/res/talks.json")
ds=dataContainer(songs=songs,talks=talks,musics=[],templstes=[])
ts=TopState(ds)


import phone.phone_gui
phone.phone_gui.init(ts)
phone.phone_gui.start()
