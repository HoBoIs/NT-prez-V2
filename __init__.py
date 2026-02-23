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
from state.template import readTemplates
c=conf.readConfig()
conf.writeConfig(c)
app = QApplication(sys.argv)
bridge=QtBridge()

#TODO: load thoings properly
songs=readSongs(c.songDir)
templates=readTemplates(c.templateDir)
images=image.importImages(c.imageDir,c)
imagesBeforeSong=[i for i in images if i.path.split("/")[-1] in c.imagesBeforeSong]
imagesAfterSong=[i for i in images if i.path.split("/")[-1] in c.imagesAfterSong]
talks=talk.readTalks("./res/talks.json",templates)
ds=dataContainer(
        songs=songs,
        talks=talks,
        musics=[],#TODO
        templstes=templates,
        images=images,
        imagesAfterSongs=imagesAfterSong,
        imagesBeforeSongs=imagesBeforeSong)
ts=TopState(ds)


import phone.phone_gui
phone.phone_gui.init(ts,bridge)
#phone.phone_gui.start()
threading.Thread(target=phone.phone_gui.start, daemon=True).start()
print("Starting QT:")
win=mw.MainWindow(ts)
win.show()
win.addBridge((bridge))
app.exec()
