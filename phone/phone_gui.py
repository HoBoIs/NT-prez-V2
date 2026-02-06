from flask import Flask, render_template,request, jsonify
app = Flask(__name__)

songs = [{"text":"S"+str(i),"searchData":"S"+str(i)+"fr"+str(i)} for i in range(30)]
talks = [{"text":"T"+str(i),"searchData":"T"+str(i)+"fr"+str(i)} for i in range(30)]
musics = [{"text":"M"+str(i),"searchData":"S"+str(i)+"fr"+str(i)} for i in range(30)]
templates =[
        {"text:":"T0","searchData":"T0","fields":2},
        {"text:":"T1","searchData":"T1","fields":1},
        {"text:":"T2","searchData":"T2","fields":1}
        ]

x="||"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        clicked = request.form["item"]
        print("Clicked:", clicked)

    return render_template("index.html", songs=songs,talks=talks,x=x)
@app.route("/SongList")
def get_items():
    return jsonify(songs)
@app.route("/TemplateList")
def get_items_4():
    return jsonify(templates)
@app.route("/TalkList")
def get_items_2():
    return jsonify(talks)
@app.route("/MusicList")
def get_items_3():
    return jsonify(musics)
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
app.run(host="0.0.0.0",debug=True)
