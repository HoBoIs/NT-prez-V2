from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout, QPlainTextEdit, QDialogButtonBox, \
    QDialog

from display.signals import QtBridge
from display.songOrder import FilterableComboBox
from state.song import Song


class OkDialog(QDialog):
    """
    nothing more than just saying OK
    """
    def __init__(self, message):
        super().__init__()

        self.setWindowTitle(message)

        QBtn = (
            QDialogButtonBox.StandardButton.Ok
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()
        message = QLabel(message)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

"""
loading widget terv

-új dal gomb üres Song-ot és invalid ID-t (-1) ad
-dal keresése funkció valid ID-t és az adott Song objektumot ad

dal keresős rész:
-dal betöltése gomb -> indítja a lyrics editort
-dal törlése a listából -> popup window

végén aktiválja a lyrics editor widgetet (connect)
deaktiválja saját magát
"""


class LoadingWidget(QWidget):
    def __init__(self, parent, top_state):
        super().__init__(parent)
        self.state = top_state

        # set up the widget layout
        self.layout_ = QGridLayout(self)
        self.setLayout(self.layout_)

        # set up song search widget
        self.selector_label = QLabel("Dalkereső")
        song_list = [("|".join(song.titles), song) for song in self.state.data.songs.values()]
        self.selector = FilterableComboBox(self, song_list, "")

        # set up button widgets
        self.newSongButton = QPushButton("új dal létrehozása")
        self.loadSongButton = QPushButton("dal betöltése")
        self.deleteSongButton = QPushButton("dal törlése a listából")

        # put up the scene (might need some refinement here)
        self.layout_.addWidget(self.newSongButton, 0,3)
        self.layout_.addWidget(self.loadSongButton, 0,1)
        self.layout_.addWidget(self.deleteSongButton, 0,2)
        self.layout_.addWidget(self.selector_label, 0,0)
        self.layout_.addWidget(self.selector, 1,0, 1, 4)

        # connect buttons
        self.newSongButton.clicked.connect(self.launchEmptyEditor)
        self.loadSongButton.clicked.connect(self.launcEditor)
        self.deleteSongButton.clicked.connect(self.deleteSong)

        # connect song selector
        self.selector.currentTextChanged.connect(self.findSong)

        # start with buttons off
        self.deactivateButtons()

    def addBridge(self, bridge):
        self.bridge = bridge
        bridge.stateUpdated.connect(self.refresh_ui)

    def activateButtons(self):
        self.loadSongButton.setEnabled(True)
        self.deleteSongButton.setEnabled(True)

    def deactivateButtons(self):
        self.loadSongButton.setEnabled(False)
        self.deleteSongButton.setEnabled(False)

    def findSong(self, title: str):
        # find matching index
        index = self.selector.findText(title, Qt.MatchFlag.MatchExactly)

        # turn on editing ability if song is properly selected
        if index >= 0:
            self.songToEdit = self.selector.itemData(index, Qt.ItemDataRole.UserRole)
            self.activateButtons()
        else:
            self.deactivateButtons()

    def connectEditor(self, editorLauncherFunction):
        self.editorLauncherFunction = editorLauncherFunction

    def launcEditor(self):
        self.editorLauncherFunction(self.songToEdit)
        self.setEnabled(False)

    def launchEmptyEditor(self):
        self.editorLauncherFunction(Song(["cím1"], ["verse1"], -1))
        self.setEnabled(False)

    def deleteSong(self):
        # TODO remove song from topstate and disk
        self.bridge.stateUpdated.emit()

    def refresh_ui(self):
        # safe-delete selector
        self.layout_.removeWidget(self.selector)
        self.selector.deleteLater()

        # reload and restore selector
        song_list = [("|".join(song.titles), song) for song in self.state.data.songs.values()]
        self.selector = FilterableComboBox(self, song_list, "")
        self.layout_.addWidget(self.selector, 1, 0, 1, 4)
        self.selector.currentTextChanged.connect(self.findSong)

        # reset buttons
        self.deactivateButtons()

"""
lyrics editor wigdet terv
kezdetben inaktív
loading widget aktiválja

aktiváláskor:
-kap egy Song objectet
-kap egy ID-t: ez lehet invalid is (új dal esetén)

szerkesztés:
-soronként beírós a cím (csak a nemüres sorokat fogadja el, min 1)
-versszakszerkesztő textbox

mentési opciók: 
-felülírás csak valid ID esetén
-mentés új dalként
-elvetés

mentés menete:
-kiírja jsonbe
-berakja a topstate dallistájába
-sikeres mentésről egy OK-gombos popup ablakot küld

mentés után:
-aktiválja a loading widgetet
-nem deaktiválja magát
-ha bármelyik textboxba (title, verses) beleírnak, deaktiválja a loading widgetet
"""

class EditorWidget(QWidget):
    def __init__(self, parent, top_state):
        super().__init__(parent)
        self.state = top_state
        self.setEnabled(False)

        # define buttons
        self.saveNewButton = QPushButton("Mentés új dalként")
        self.saveOverButton = QPushButton("Dal mentése (felülír)")
        self.cancelButton = QPushButton("Módosítások elvetése")

        # feedback widgets
        self.titleLabel = QLabel()
        self.versesLabel = QLabel()

        # editor widgets
        self.titleText = QPlainTextEdit()
        self.versesText = QPlainTextEdit()

        # set layout
        self.layout_ = QGridLayout(self)
        self.setLayout(self.layout_)

        # arrange widget
        self.layout_.addWidget(self.titleLabel, 0, 0)
        self.layout_.addWidget(self.titleText, 0, 1, 1, 2)
        self.layout_.addWidget(self.versesLabel, 1, 0)
        self.layout_.addWidget(self.versesText, 1, 1, 1, 2)
        self.layout_.addWidget(self.saveNewButton, 2, 0)
        self.layout_.addWidget(self.saveOverButton, 2, 1)
        self.layout_.addWidget(self.cancelButton, 2, 2)

        # connect functions
        self.saveNewButton.clicked.connect(self.saveNew)
        self.saveOverButton.clicked.connect(self.saveOver)
        self.cancelButton.clicked.connect(self.cancel)

        self.titleText.textChanged.connect(self.checkTitles)
        self.versesText.textChanged.connect(self.checkVerses)

    def addBridge(self, bridge):
        self.bridge = bridge

    def startEditing(self, song):
        self.setEnabled(True)
        self.song = song

        # set up editor
        self.titleText.setPlainText("\n".join(song.titles))
        self.versesText.setPlainText((3*"\n").join(map(str.strip, song.verses)))

        self.saveOverButton.setEnabled(song._id != -1)

    def readyToSave(self, new = False):
        """
        check if song titles do not clash
        :return: False if song all titles exist, True if song is ready to be saved
        """
        if self.titleText.toPlainText().strip() == "":
            return False

        for title in self.titleText.toPlainText().strip().split("\n"):
            mathced_song = self.state.findSong(title)
            if mathced_song is None or (not new and mathced_song._id == self.song._id):
                return True

        return False
    def checkTitles(self):
        # TODO update corresponding QLabel to show title1, title2, etc
        self.enableLoader(False)

    def checkVerses(self):
        # TODO update corresponding QLabel to show how the 3*"\n" separates the verses
        self.enableLoader(False)

    def connectLoader(self, enableLoader):
        self.enableLoader = enableLoader

    def saveNew(self):
        if not self.readyToSave(new=True):
            dial = OkDialog("Sikertelen mentés: ilyen című dal már létezik!")
            dial.exec()
            return

        # create new song ID
        self.song._id = max(self.state.data.songs.keys(), default=0) + 1

        self.saveOver()

    def saveOver(self):
        if not self.readyToSave():
            dial = OkDialog("Sikertelen mentés: ilyen című dal már létezik!")
            dial.exec()
            return

        self.song.titles = list(map(str.strip, self.titleText.toPlainText().strip().split("\n")))
        self.song.verses = list(map(str.strip, self.versesText.toPlainText().strip().split(3*"\n")))

        self.state.data.songs[self.song._id] = self.song
        self.bridge.stateUpdated.emit()

        # TODO save to disk in json format
        dial = OkDialog("Sikeres Mentés")
        dial.exec()

        # most már létezik ez a dal
        self.saveOverButton.setEnabled(True)

        # loadert újraindítjuk
        self.enableLoader(True)



    def cancel(self):
        self.setEnabled(False)

        self.titleText.setPlainText("")
        self.versesText.setPlainText("")

        self.enableLoader(True)



class SongEditorWindow(QWidget):
    def __init__(self, top_state):
        super().__init__()
        self.state = top_state

        # set up the window
        self.setWindowTitle("Dalszerkesztő")
        self.layout_ = QVBoxLayout(self)
        self.setLayout(self.layout_)

        # add widgets
        self.loadingWidget = LoadingWidget(parent=self, top_state=top_state)
        self.editingWidget = EditorWidget(parent=self, top_state=top_state)

        # connect functions
        self.loadingWidget.connectEditor(self.editingWidget.startEditing)
        self.editingWidget.connectLoader(self.loadingWidget.setEnabled)

        self.layout_.addWidget(self.loadingWidget)
        self.layout_.addWidget(self.editingWidget)


    def addBridge(self, bridge: QtBridge):
        bridge.stateUpdated.connect(self.refresh_ui)
        self.loadingWidget.addBridge(bridge)
        self.editingWidget.addBridge(bridge)

    def refresh_ui(self):
        pass