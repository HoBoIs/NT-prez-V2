from state.songReader import readSongs
from state.topState import TopState, dataContainer
import state.talk as talk
import threading
from PyQt6.QtWidgets import QApplication
import sys
import display.mainWindow as mw
from display.signals import QtBridge
app = QApplication(sys.argv)
bridge=QtBridge()

#TODO: load thoings properly
songs=readSongs("./state/res/songs/")
talks=talk.readTalks("./state/res/talks.json")
ds=dataContainer(songs=songs,talks=talks,musics=[],templstes=[])
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
