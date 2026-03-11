from PyQt6.QtCore import QUrl, QEventLoop
from PyQt6.QtMultimedia import QMediaPlayer

def detectMediaType(path):
    player = QMediaPlayer()
    loop = QEventLoop()

    def on_status_changed(status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            loop.quit()
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            loop.quit()

    player.mediaStatusChanged.connect(on_status_changed)
    player.setSource(QUrl.fromLocalFile(path))

    loop.exec()

    has_video = len(player.videoTracks()) > 0
    has_audio = len(player.audioTracks()) > 0

    if has_video:
        return "video"
    elif has_audio:
        return "audio"
    else:
        return "error"
