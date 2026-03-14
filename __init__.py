from display.setupWindow import SetupWindow
from state.songReader import readSongs
from state.topState import TopState, dataContainer
import state.talk as talk
import threading
from PyQt6.QtWidgets import QApplication
import sys
import display.mainWindow as mw
import state.imageState as image
from display.signals import QtBridge
import state.config as conf
import os
from state.template import readTemplates
from state.songOrderIO import readSongOrder
c=conf.readConfig()
conf.writeConfig(c)
app = QApplication(sys.argv)
bridge=QtBridge()
if os.path.isdir(c.musicDir):
    musics=os.listdir(c.musicDir)
else:
    musics=[]
#TODO: load thoings properly
songs=readSongs(c.songDir)
templates=readTemplates(c.templateDir)
images=image.importImages(c.imageDir,c)
imagesBeforeSong=[i for i in images if i.path.split("/")[-1] in c.imagesBeforeSong]
imagesAfterSong=[i for i in images if i.path.split("/")[-1] in c.imagesAfterSong]
talks=talk.readTalks("./res/talks.json",list(templates.values()),c.talkMediaDir)
ds=dataContainer(
        songs=songs,
        talks=talks,
        musics=musics,
        templstes=templates,
        images=images,
        imagesAfterSongs=imagesAfterSong,
        imagesBeforeSongs=imagesBeforeSong,
        songOrder=[])
so=readSongOrder("./res/songOrder.json",ds)#TODO config
ds.songOrder=so
ts=TopState(ds,c)


import phone.phone_gui
phone.phone_gui.init(ts,bridge)
#phone.phone_gui.start()
threading.Thread(target=phone.phone_gui.start, daemon=True).start()
print("Starting QT:")
win=mw.MainWindow(ts)
win2=SetupWindow(ts)
win.show()
win2.show()
win.addBridge((bridge))
win2.addBridge(bridge)
app.exec()
