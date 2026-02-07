from dataclasses import dataclass
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
from server.song import Song
import server.topState

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
    return render_template("index.html")
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
    data = request.json
    print('got:',data)
    return {"ok": True}
    
@app.route("/sendSong", methods=["POST"])
def sendsong():
    data = request.json
    print("Clicked:", data)
    return {"ok": True}

def start():
    app.run(host="0.0.0.0",debug=True)
