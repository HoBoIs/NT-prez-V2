from dataclasses import dataclass
from re import T
from flask import Flask,request,render_template
from flask_socketio import SocketIO, emit
import json

from state.talkState import TalkState
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") #disable monitoring?
from state.talk import Talk
from state.song import Song, SongListState, SongState
import state.topState as topState
import time
from display.signals import QtBridge
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
@dataclass
class ComState:
    songs:list[dict[str,str|list[str]]]
    talks:list[dict[str,str]]
    music:list[dict[str,str]]
    templates:list[dict[str,str]]
    def refreshFromState(self,st:topState.TopState):
        self.songs=[transformSong(s) for s in st.data.songs]
        self.talks=[transformTalk(s) for s in st.data.talks]
        self.musics=[transformMusic(s) for s in st.data.musics]
state : topState.TopState
lstate: ComState
bridge:QtBridge
def init(ts :topState.TopState,b:QtBridge):
    global state
    global bridge
    bridge=b
    state=ts
    global lstate
    lstate=ComState([],[],[],[])
    lstate.refreshFromState(state)
def transformTalk(t:Talk):
    res:dict[str,str] ={}
    res["text"]=t.title+" "+t.name
    res["searchData"]=res["text"]
    return res

def transformSong(s:Song):
    res:dict[str,str|list[str]] ={}
    res["text"]=s.titles[0]
    res["titles"]=s.titles
    res["verses"]=s.verses
    #res["searchData"]="\n".join(s.titles)+"\n---\n"+"\n\n".join(s.verses)
    return res
def transformMusic(m:str):
    return {"text":m,"searchData":m}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        clicked = request.form["item"]
        print("Clicked:", clicked)
    #return render_template("index.html", songs=songs,talks=talks)
    return render_template("index.html")

def sendSongs():
    emit("songs",lstate.songs)
def sendTemplates():
    emit("templates",lstate.templates)
def sendTalks():
    emit("talks",lstate.talks)
def sendMusics():
    emit("musics",lstate.talks)
def onchange(kind):
    pass
@socketio.on("connect")
def on_connect():
    sendSongs()
    sendTalks()
    sendTemplates()
    sendMusics()
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
            pass
        elif txt=="Pause":
            pass
        elif txt=="Stop":
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
    
def inc(x:float,sign:str,y:float):
    d=0.02 if sign=="+" else -0.02
    x+=d
    if x<0: return 0
    return min(0.95-y,x)


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
        bridge.stateUpdated.emit("")
def sendSongState():
  if (isinstance(state._state,SongListState)):
      si=state._state.SongIdx
      if type(state._state.childState)==SongState:
          vi=state._state.childState.verseIdx
          emit("songSelected",{"songidx":si,"vidx":vi},broadcast=True)
      else:
          emit("songSelected",{"songidx":si,"vidx":-1},broadcast=True)

@socketio.on("command")
def command(data):
    with state._lock:
        data=json.loads(data)
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return
        txt=data["text"]
        if txt=="Next":
            state._state.nextState()
            sendSongState()
            bridge.stateUpdated.emit("")
        elif txt=="Prev":
            state._state.prevState()
            bridge.stateUpdated.emit("")
            sendSongState()
        elif txt=="Skip":
            pass
        elif txt=="Empty":
            pass
        elif txt=="Music":
            pass
        elif txt=="Thanks":
            for s in state._state.getChain():
                if isinstance(s,TalkState):
                    s.toThanks()
                    bridge.stateUpdated.emit("")
        elif txt=="Invert":
            state._opts.inversion=not state._opts.inversion
            bridge.stateUpdated.emit("")
        #TODO: notify

@socketio.on("talkSet")
def sendTalk(data):
    with state._lock:
        data=json.loads(data)
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return 
        print(data)
        pres_idx=data['index']
        pres_txt=data['text']

        if lstate.talks[pres_idx]['text']!=pres_txt:
            sendSongs()
            return
        state._state=TalkState(state,state.data.talks[pres_idx])
        emit("talkSelected",{"talkidx":data['index']},broadcast=True)
        bridge.stateUpdated.emit("")

@socketio.on("songSet")
def sendsong(data):
    with state._lock:
        data=json.loads(data)
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return 
        pres_idx=data['index']
        pres_txt=data['text']
        if lstate.songs[pres_idx]['text']!=pres_txt:
            sendSongs()
            return
        state._state=SongListState(state,state.data.songs,pres_idx,data["verseIdx"])
        emit("songSelected",{"songidx":data['index'],"vidx":data["verseIdx"]},broadcast=True)
        #print(state._state.childState)
        bridge.stateUpdated.emit("")
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
def start():
    if (state.cfg.server):
        socketio.run(app,host="0.0.0.0", debug=False,use_reloader=False,port=find_free_port())
    else:
        socketio.run(app,debug=False,use_reloader=False,port=find_free_port())
    #app.run(host="0.0.0.0",debug=True)
