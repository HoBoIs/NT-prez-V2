from dataclasses import asdict, dataclass
from flask import Flask,request,render_template
from flask_socketio import SocketIO, emit
import json

from state.custumState import ClampedSongState
from state.image import Image
from state.songOrder import SongOrder
from state.talkState import TalkState
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*",ping_interval=10) #disable monitoring?
from state.talk import Talk
from state.song import Song
from state.songState import SongState
import state.topState as topState
import time
from display.signals import QtBridge,MEvent
import socket
name="Web"
lastUsedBy='INVALIDIP'
lastUsedTime=0
def shouldIgnore(ip,gottime):
    global lastUsedBy
    global lastUsedTime
    if ip!=lastUsedBy and time.time()-lastUsedTime < 2:
        return True
    if (gottime-time.time()*1000)>5000:
        return True
    lastUsedBy=ip
    lastUsedTime=time.time()
    return False
volume=0

def getElement(ls:list[int],idx:int)->int:
    return ls[idx] if idx<len(ls) else 0

@dataclass
class ElementItem:
    text : str
    kind:str
    titles: None | list[str] 
    basicSearchData: str 
    detailedSearchData: str
    music: None | str 
    parts:None | list["ElementItem"] 
    def __init__(self,kind:str,text:str,parts:list["ElementItem"]|None=None,titles:list[str]|None=None,basicSearchData:str|None=None,detailedSearchData:str|None=None,music:str|None=None) -> None:
        self.kind=kind
        self.text=text
        self.parts=parts
        self.titles=titles
        if basicSearchData != None:
            self.basicSearchData= basicSearchData
        elif titles != None:
            self.basicSearchData="|".join(titles)
        else:
            self.basicSearchData=text
        if detailedSearchData != None:
            self.detailedSearchData=detailedSearchData
        elif parts:
            self.detailedSearchData=self.basicSearchData+"|"+"|".join([p.detailedSearchData for p in parts])
        else:
            self.detailedSearchData=self.basicSearchData
        self.music=music


@dataclass
class ComState:
    songs:list[ElementItem]
    talks:list[ElementItem]
    music:list[ElementItem]
    templates:list[dict[str,str]]
    songOrder:list[ElementItem]
    idxs:list[int]
    mode:str=""
    def __init__(self,st:topState.TopState):
        self.refreshFromState(st)
        self.templates=[]
        self.mode=""
        self.idxs=[]
    def refreshFromState(self,st:topState.TopState):
        self.songs=[transformSong(s) for s in st.data.songs.values()]
        self.talks=[transformTalk(s) for s in st.data.talks.values()]
        self.musics=[transformMusic(s) for s in st.data.musics]
        self.songOrder=[transformSongOrder(s,st.data) for s in st.data.songOrder]
state : topState.TopState
lstate: ComState
bridge:QtBridge
def init(ts :topState.TopState,b:QtBridge):
    global state
    global bridge
    bridge=b
    state=ts
    global lstate
    lstate=ComState(state)
def transformTalk(t:Talk)->ElementItem:
    parts=[ElementItem("Title",t.title+" "+t.name)] +\
            [ElementItem("Picture", p) for p in t.pictures]+\
            ([ElementItem("Title", t.title+" "+t.name)] if t.pictures else []) +\
            ([ElementItem("Song",t.thanks[0].titles[0]+ "|" + ",".join (t.thanks[1]) )] if t.thanks[0].titles else []) +\
            ([ElementItem("Song",t.media.musicSong)] if t.media.musicSong else [])

    return ElementItem("talk",t.name+" | "+t.title,parts,music=(t.media.path if t.media.path else None ))

def transformSongOrder(s:topState.SongOrderItem, d:topState.dataContainer) -> ElementItem:
    match s.data:
        case Song():
            return transformSong(d.songs[s._id])
        case Talk():
            return transformTalk(d.talks[s._id])
        case _:
            assert_never(data)
def transformSong(s:Song) -> ElementItem:
    return ElementItem("song",s.titles[0],[ElementItem("verse",v) for v in s.verses],s.titles)
def transformMusic(m:str) -> ElementItem:
    return ElementItem("Music",m,music=m)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        clicked = request.form["item"]
        print("Clicked:", clicked)
    #return render_template("index.html", songs=songs,talks=talks)
    return render_template("index.html")

def sendSongOrder(broadcast=False):
    emit("songOrder",[asdict(s) for s in lstate.songOrder],broadcast=broadcast)
def sendSongs(broadcast=False):
    emit("songs",[asdict(s) for s in lstate.songs],broadcast=broadcast)
def sendTemplates(broadcast=False):
    emit("templates",lstate.templates,broadcast=broadcast)
def sendTalks(broadcast=False):
    emit("talks",[asdict (s) for s in lstate.talks],broadcast=broadcast)
def sendMusics(broadcast=False):
    emit("musics",[asdict(s) for s in lstate.talks],broadcast=broadcast)
def onchange(kind):
    pass
@socketio.on("connect")
def on_connect():
    sendSongs()
    sendSongOrder()
    sendTalks()
    sendTemplates()
    sendMusics()
    sendPreviews()
    emit("volume",state._opts.Volume)
    emit("Auto",state._opts.autoPlay)


@socketio.on("soundSet")
def onSondSet(data):
    with state._lock:
        data=json.loads(data)
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return 
        print('got:',data)
        txt : str=data["text"]
        if txt=="Play":
            bridge.mediaEvent.emit(MEvent.START)
            pass
        elif txt=="Pause":
            bridge.mediaEvent.emit(MEvent.PAUSE)
            pass
        elif txt=="Stop":
            bridge.mediaEvent.emit(MEvent.STOP)
            pass
        elif txt.startswith("Auto:"):
            print(txt)
            if txt=="Auto:true":
                state._opts.autoPlay=True
            else:
                state._opts.autoPlay=False
            emit("Auto",state._opts.autoPlay,broadcast=True)
        elif txt.startswith("Volume:"):
            state._opts.Volume=int(txt[7:])
            emit("volume",state._opts.Volume,broadcast=True)
            bridge.stateUpdated.emit()
    
def inc(x:float,sign:str,y:float):
    d=0.02 if sign=="+" else -0.02
    x+=d
    if x<0: return 0
    return min(0.95-y,x)

@socketio.on('stateUpdated')
def handle_update(json):
    print("UPDATED",json)
    global lstate
    lstate.refreshFromState(state)
    sendSongs(True)
    sendSongOrder(True)
    sendTalks(True)
    sendTemplates(True)
    sendMusics(True)
    sendPreviews()
    emit("volume",state._opts.Volume,broadcast=True)
    emit("Auto",state._opts.autoPlay,broadcast=True)

@socketio.on("margin")
def marginSet(data):
    with state._lock:
        data=json.loads(data)
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return
        txt=data["text"]
        if txt=="Reset":
            state.margins=topState.Margins(0,0,0,0)
        elif txt[0]=='L':
            state.margins.left=inc(state.margins.left,txt[1],state.margins.right)
        elif txt[0]=='T':
            state.margins.top=inc(state.margins.top,txt[1],state.margins.bottom)
        elif txt[0]=='B':
            state.margins.bottom=inc(state.margins.bottom,txt[1],state.margins.top)
        elif txt[0]=='R':
            state.margins.right=inc(state.margins.right,txt[1],state.margins.left)
        bridge.stateUpdated.emit()

def sendStateToPhones(c:str,i:int,j:int):
    emit("Selected",{"mainIdx":i,"subIdx":j,"chanel":c})

@socketio.on("command")
def command(data):
    with state._lock:
        data=json.loads(data)
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return
        txt=data["text"]
        if txt=="Next":
            state._state.nextState()
            bridge.stateUpdated.emit()
        elif txt=="Prev":
            state._state.prevState()
            bridge.stateUpdated.emit()
        elif txt=="Skip":
            state._state.childEndedNxt()
            bridge.stateUpdated.emit()
            pass
        elif txt=="Empty":
            pass
        elif txt=="PlayPause":
            for s in state._state.getChain():
                if isinstance(s,TalkState):#TODO rework for generalisation
                    bridge.mediaEvent.emit(MEvent.PLAYPAUSE)
        elif txt=="Music":
            for s in state._state.getChain():
                if isinstance(s,TalkState):
                    bridge.mediaEvent.emit(MEvent.PLAYPAUSE)
        elif txt=="Thanks":
            for s in state._state.getChain():
                if isinstance(s,TalkState):
                    s.toThanks()
                    bridge.stateUpdated.emit()
        elif txt=="Invert":
            state._opts.inversion=not state._opts.inversion
            bridge.stateUpdated.emit()
        if lstate.mode=="songOrder":
            lstate.idxs=state._state.getIdxsForFL()
        else:
            lstate.idxs=[lstate.idxs[0]] + state._state.getIdxsForFL()
        sendPreviews()
        #TODO: notify

@socketio.on("talkSet")
def sendTalk(data):
    with state._lock:
        data=json.loads(data)
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return
        indexes:list[int]=data['indexes']
        pres_idx:int=indexes[0]
        pres_txt:str=data['text']

        if lstate.talks[pres_idx].text!=pres_txt:
            sendTalks()
            return
        state._state=TalkState(state,state.data.talks[pres_idx])
        state._state.setIndex(getElement( indexes,1))
        if state.media and isinstance(state.media.descript.parent,TalkState):
            p=state.media.descript.parent
            if p.talk.title == state.data.talks[pres_idx].title and p.talk.name == state.data.talks[pres_idx].name:
                state.media.descript.parent=state._state
                state.media.descript.adEnfFun=state._state.toThanks
        lstate.mode="talk"
        lstate.idxs=data['indexes']+[0,0,0,0]
        #emit("talkSelected",{"talkidx":data['indexes']},broadcast=True)
        sendPreviews()
        bridge.stateUpdated.emit()

@socketio.on("songOrderSet")
def sendsongOrder(data):
    with state._lock:
        data=json.loads(data)
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return 
        pres_idx:int=data['indexes'][0]
        pres_txt:str=data['text']
        print(data)
        if lstate.songOrder[pres_idx].text!=pres_txt:
            sendSongOrder()
            return
        state._state=SongOrder(state,[x.cnst for x in state.data.songOrder])
        state._state.setIndex(pres_idx)
        if len(data['indexes'])>1 and state._state.childState:
            state._state.childState.setIndex(getElement(data["indexes"],1))
        #SongListState(state,list(state.data.songs.values()),pres_idx,data["verseIdx"])
        #emit("songSelected",{"songidx":data['index'],"vidx":data["verseIdx"]},broadcast=True)
        lstate.mode="songOrder"
        lstate.idxs=data['indexes']+[0,0,0,0]
        #print(state._state.childState)
        sendPreviews()
        bridge.stateUpdated.emit()

def sendPreviews():
    s=state.getBonnomState()
    m=state.getMedia()
    md:dict[str,str|float]
    if m:
        md={"name":m.descript.path,"length":m.length/1000,"status":m.status,"infoDate":m.infoDate,"age":m.age/1000}
    else:
        md={"name":"-"}
    d={"prev":s.prevPreview(),"act":s.actPreview(),"next":s.nextPreview(),"media":md,"indexes":lstate.idxs,"mode":lstate.mode}
    emit("previews",d,broadcast=True)

@socketio.on("songSet")
def sendsong(data):
    with state._lock:
        data=json.loads(data)
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return 
        pres_idx:int=data['indexes'][0]
        pres_txt:str=data['text']
        if lstate.songs[pres_idx].text !=pres_txt:
            sendSongs()
            return
        state._state=ClampedSongState(state,
                                      list(state.data.songs.values())[pres_idx],
                                      Image(""),subIdx=getElement(data["indexes"],1))
        lstate.mode="song"
        lstate.idxs=data['indexes']+[0,0,0,0]
        #emit("songSelected",{"songidx":data['index'],"vidx":data["verseIdx"]},broadcast=True)
        sendPreviews()
        #print(state._state.childState)
        bridge.stateUpdated.emit()
'''
def find_free_port(start_port=8000, max_tries=40):
    port = start_port
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                print("using port:",port)
                return port
            except OSError:
                port += 1
    raise RuntimeError("No free ports available")
'''

def start():
    import logging
    #logging.getLogger('werkzeug').setLevel(logging.ERROR)
    if (state.cfg.server):
        host='0.0.0.0'
    else:
        host='127.0.0.1'
    for i in range(20):
        try:
            state.port=8000+i
            state.ip=host
            socketio.run(app,host=host, debug=False,use_reloader=False,port=8000+i)
        except:
            print("port",8000+i ,"is unusable")
            pass
    #app.run(host="0.0.0.0",debug=True)
'''
import psutil
import socket

addrs = psutil.net_if_addrs()

for interface, addr_list in addrs.items():
        for addr in addr_list:
                if addr.family == socket.AF_INET:
                            print(f"{interface}: {addr.address}")'''
