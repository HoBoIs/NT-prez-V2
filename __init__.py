from server.songReader import readSongs
from server.topState import TopState, dataContainer
import server.talk as talk
songs=readSongs("./server/res/songs/")
talks=talk.readTalks("./server/res/talks.json")
ds=dataContainer(songs=songs,talks=talks,musics=[],templstes=[])
ts=TopState(ds)


import phone.phone_gui
phone.phone_gui.init(ts)
phone.phone_gui.start()
