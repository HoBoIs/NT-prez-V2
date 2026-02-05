from flask import Flask, render_template,request, jsonify
app = Flask(__name__)

songs = [{"text":"S"+str(i)} for i in range(30)]
talks = [{"text":"T"+str(i)} for i in range(30)]
musics = [{"text":"M"+str(i)} for i in range(30)]

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
