from PyQt6.QtGui import QPixmap,QImage,QColor
import numpy as np
import state.image
from typing import cast

def makeInverse(pmap:QPixmap):
    img = pmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
    w, h = img.width(), img.height()
    ptr = img.bits()
    if ptr==None: # NEVER
        return pmap
    ptr.setsize(img.sizeInBytes())
    arr = np.frombuffer(cast(memoryview ,ptr),dtype= np.uint8).reshape((h, w, 4))
    arr[..., :3] = 255 - arr[..., :3]
    return QPixmap.fromImage(img)

def makeGradiante(pmap: QPixmap, color_a: QColor, color_b: QColor):
    img = pmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
    w, h = img.width(), img.height()
    ptr = img.bits()
    if ptr==None: # NEVER
        return pmap
    ptr.setsize(img.sizeInBytes())
    arr = np.frombuffer(cast(memoryview ,ptr),dtype= np.uint8).reshape((h, w, 4))
    bgr = arr[..., :3].astype(np.float32)
    A = np.array([color_a.blue(), color_a.green(), color_a.red()], dtype=np.float32)
    B = np.array([color_b.blue(), color_b.green(), color_b.red()], dtype=np.float32)
    lum = (0.114 * bgr[..., 0] + 0.587 * bgr[..., 1] + 0.299 * bgr[..., 2]) / 255.0
    out = A + lum[..., None] * (B - A)
    arr[..., :3] = np.clip(out, 0, 255).astype(np.uint8)
    return QPixmap.fromImage(img)

class DisplayImage:
    data:state.image.Image
    img:QPixmap
    invImg:QPixmap
    def __init__(self,d:state.image.Image):
        self.data=d
        if d.invertable:
            tmp=QPixmap(d.path)
            self.img=tmp
            self.invImg=makeInverse(tmp)
        else:
            self.img=QPixmap(d.path)
            self.invImg=QPixmap(d.path)
