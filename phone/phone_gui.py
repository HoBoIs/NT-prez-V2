from dataclasses import dataclass
from flask_socketio import SocketIO, emit
from flask import Flask, render_template,request, jsonify
#from typing import TYPE_CHCKING
app = Flask(__name__)
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
@app.route("/SongList")
def get_items():
    return jsonify(lstate.songs )
@app.route("/TemplateList")
def get_items_4():
    return jsonify(lstate.templates)
@app.route("/TalkList")
def get_items_2():
    return jsonify(lstate.talks)
@app.route("/MusicList")
def get_items_3():
    return jsonify(lstate.musics)
@app.route("/sendTalk", methods=["POST"])
def sendtalk():
    data = request.json
    print("Clicked2:", data)
    return {"ok": True}

@app.route("/soundSet", methods=["POST"])
def onSondSet():
    with state._lock:
        data = request.json
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return {"ok": True}
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
    return {"ok": True}
    

@app.route("/command", methods=["POST"])
def command():
    with state._lock:
        data = request.json
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return {"ok": True}
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
        return {"ok": True}

@app.route("/sendSong", methods=["POST"])
def sendsong():
    with state._lock:
        data = request.json
        if (shouldIgnore(request.remote_addr,data["sent_at"])):
            return {"ok": True}
        pres_idx=data['index']
        pres_txt=data['text']
        if lstate.songs[pres_idx]['text']!=pres_txt:
            #TODO allert old data
            return {"ok": True}
        state._state=SongListState(state,state.data.songs,pres_idx)
        #print(state._state.childState)
    return {"ok": True}

def start():
    app.run(host="0.0.0.0",debug=True)
