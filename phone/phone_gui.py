from dataclasses import dataclass
#from flask import Flask, render_template,request, jsonify
from flask import Flask,request,render_template
from flask_socketio import SocketIO, emit
#from typing import TYPE_CHCKING
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*") #disable monitoring?
"""
songs = [{"text":"S"+str(i),"searchData":"S"+str(i)+"fr"+str(i)} for i in range(30)]
talks = [{"text":"T"+str(i),"searchData":"T"+str(i)+"fr"+str(i)} for i in range(30)]
musics = [{"text":"M"+str(i),"searchData":"S"+str(i)+"fr"+str(i)} for i in range(30)]
templates =[
        {"text:":"T0","searchData":"T0","fields":2},
        {"text:":"T1","searchData":"T1","fields":1},
        {"text:":"T2","searchData":"T2","fields":1}
        ]
"""
#st=server.topState.TopState(data=server.topState.dataContainer([Song(["Cim1"],["V1"],""),Song(["Cim2"],["V1","V2","V3"],"")],[],["m1.mpx","m2.mpx"]))
#songs=[transformSong(s) for s in st.data.songs]
from server.talk import Talk
from server.song import Song, SongListState
import server.topState
import time

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
    songs:list[dict[str,str]]
    talks:list[dict[str,str]]
    music:list[dict[str,str]]
    templates:list[dict[str,str]]
    def refreshFromState(self,st:server.topState.TopState):
        self.songs=[transformSong(s) for s in st.data.songs]
        self.talks=[transformTalk(s) for s in st.data.talks]
        self.musics=[transformMusic(s) for s in st.data.musics]
state : server.topState.TopState
lstate: ComState
def init(ts :server.topState.TopState):
    global state
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
    res:dict[str,str] ={}
    res["text"]=s.titles[0]
    res["searchData"]="\n".join(s.titles)+"\n---\n"+"\n\n".join(s.verses)
    return res
def transformMusic(m:str):
    return {"text":m,"searchData":m}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        clicked = request.form["item"]
        print("Clicked:", clicked)
    #return render_template("index.html", songs=songs,talks=talks)
    return render_template("index.html",volume=volume)

def sendSongs():
    emit("songs",lstate.songs)
def sendTemplates():
    emit("templates",lstate.templates)
def sendTalks():
    emit("talks",lstate.talks)
def sendMusics():
    emit("musics",lstate.talks)

@socketio.on("connect")
def on_connect():
    sendSongs()
    sendTalks()
    sendTemplates()
    sendMusics()


@socketio.on("soundSet")
def onSondSet(data):
    with state._lock:
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
            pass
        elif txt.startswith("Volume:"):
            global volume
            volume=int(txt[7:])
            print(volume)
    

@socketio.on("command")
def command(data):
    with state._lock:
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return
        txt=data["text"]
        if txt=="Next":
            state._state.nextState()
        elif txt=="Prev":
            state._state.prevState()
        elif txt=="Skip":
            pass
        elif txt=="Empty":
            pass
        elif txt=="Music":
            pass
        elif txt=="Thanks":
            pass
        elif txt=="Invert":
            pass
        #TODO: notify

@socketio.on("songSet")
def sendsong(data):
    with state._lock:
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return 
        pres_idx=data['index']
        pres_txt=data['text']
        if lstate.songs[pres_idx]['text']!=pres_txt:
            #TODO allert old data
            return 
        state._state=SongListState(state,state.data.songs,pres_idx)
        #print(state._state.childState)

def start():
    socketio.run(app,host="0.0.0.0", debug=True)
    #app.run(host="0.0.0.0",debug=True)
