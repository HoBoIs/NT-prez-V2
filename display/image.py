from PyQt6.QtGui import QPixmap,QImage,QColor
import numpy as np
from state import topState
import state.image
from typing import cast
from state.vilagSarkok import City

def normalise1(f1,f2,t1,t2,c):
    fl=f1-f2
    tl=t1-t2
    c0=c-f1
    return c0/fl*tl+t1

def makeVS(pmap:QPixmap,cities:list[City],path:str):
    if cities and cities[-1].name=="New York":
        pmap= QPixmap(path.removesuffix(path.split('/')[-1] )+'/us.svg')
        return pmap
    img = pmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
    w, h = img.width(), img.height()
    ptr = img.bits()
    if ptr==None: # NEVER
        return pmap
    ptr.setsize(img.sizeInBytes())
    arr = np.frombuffer(cast(memoryview ,ptr),dtype= np.uint8).reshape((h, w, 4))
    black_mask =  np.all(arr[...,:3] == 0, axis=2) & arr[...,3]>0
    ys, xs = np.where(black_mask)
    westMost=xs.min()
    eastMost=xs.max()
    topMost=ys.min()
    bottomMost=ys.max()
#45.73705804567691, 18.446752124733074
#48.58523187578859, 21.43949719995505
#47.956555813758385, 22.896662679691815
#46.8691264166296, 16.113533213592607
    h, w = arr.shape[:2]
    y, x = np.ogrid[:h, :w]

    mask = (x - westMost)**2 + (y - topMost)**2 <= 20**2
    last= (cities and cities[-1].name.lower()=="világ")
    for c in cities:
        r=5 if not last else 7
        cx=normalise1(16.11,22.9,westMost,eastMost,c.y)
        cy=normalise1(48.58,45.74,topMost,bottomMost,c.x)
        distance_array = 1/((x - cx)**2 + (y - cy)**2)
        arr [:,:,0]= arr[:,:,0] * (1-distance_array*r*r/1.5)
        arr [:,:,1]= arr[:,:,1] * (1-distance_array*r*r/1.5)
        arr [:,:,2]= arr[:,:,2] * (1-distance_array*r*r/1.5) # Fény kiterjedés
    for c in cities:
        r=5 if not last else 7
        cx=normalise1(16.11,22.9,westMost,eastMost,c.y)
        cy=normalise1(48.58,45.74,topMost,bottomMost,c.x)
        mask = (x - cx)**2 + (y - cy)**2 <= r**2
        arr[mask,:]=(np.array([100,100,100,255]) if not last else np.array([0,0,0,255])) # Város bejelölés
    arr [:,:,:3]=np.clip(arr[:,:,:3], 0, 255).astype(np.uint8)
    if cities and not last: #kör
        c=cities[-1]
        r=6
        cx=normalise1(16.11,22.9,westMost,eastMost,c.y)
        cy=normalise1(48.58,45.74,topMost,bottomMost,c.x)
        mask = (x - cx)**2 + (y - cy)**2 <= r**2
        arr[mask,:]=np.array([0,0,0,255])

        mask = ((r*1.5) **2<= (x - cx)**2 + (y - cy)**2) & ((x - cx)**2 + (y - cy)**2<= (r*2)**2)
        arr[mask,:]=np.array([0,10,255,255])
    return QPixmap.fromImage(img)
def makeInverseGrayScale(pmap:QPixmap):
    img = pmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
    w, h = img.width(), img.height()
    ptr = img.bits()
    if ptr==None: # NEVER
        return pmap
    ptr.setsize(img.sizeInBytes())
    arr = np.frombuffer(cast(memoryview ,ptr),dtype= np.uint8).reshape((h, w, 4))
    tolerance = 2
    gray_mask = (
        (np.abs(arr[..., 0] - arr[..., 1]) < tolerance) &
        (np.abs(arr[..., 1] - arr[..., 2]) < tolerance)
    )
    arr[gray_mask, :3] = 255 - arr[gray_mask, :3]
    return QPixmap.fromImage(img)
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
    def convert(self,ls:list[City]):
        d=self.data
        tmp=QPixmap(d.path)
        self.img=makeVS(tmp,ls,d.path)
        self.invImg=makeInverseGrayScale(self.img)
