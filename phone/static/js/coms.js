function sanitize(orig){
  return orig .toLowerCase()
              .normalize("NFD")
              .replace(/[\u0300-\u036f]/g, "")
              .replace(/[^a-z0-9]/g,"")
}

function send(chanel,msg){
  if (typeof(msg)=='string'){
    msg={'text':msg}
  }
  msg.sent_at=Date.now();
  socket.emit(chanel, JSON.stringify(msg));
}

const socket = io();
//async function loadData(chanel,data,contID){
function loadData(chanel,data,contID){
  const items = data
  const cont=document.getElementById(contID)
  cont.innerHTML=""

  for (let i=0; i<items.length; i++){
    const btn=document.createElement("button");
    btn.innerHTML = "<div>"+items[i].text+"</div>";
    btn.data = items[i]
    btn.searchData=items[i].text
    btn.onclick = () => 
      send(chanel,{"text":items[i].text,"index":i})
    cont.appendChild(btn);
    /*if (btn.data!=btn.innerText && chanel=="songSet"){
      const subBtn=document.createElement("button");
      const dv=document.createElement("div");
      dv.innerText=btn.data.titles.join('\n')+"\n---\n"+btn.data.verses.join('\n')
      dv.dataShow="none"
      subBtn.innerText="👁"
      subBtn.onclick=(event)=>{
        event.stopPropagation()
        dv.dataShow=dv.dataShow=="none"?"":"none"
        dv.style.display=dv.dataShow
      }
      dv.style.display="none"
      btn.appendChild(subBtn)
      cont.appendChild(dv)
    }*/
  }
}
function loadItem(cont,btn,chanel,idx,inner,partList){
  const text=btn.data.text
  //!!!btn.searchData
  btn.onclick = () => 
  send(chanel,{"text":text,"index":idx,"verseIdx":0})
  btn.id=chanel+" "+idx
  cont.appendChild(btn);
  const subBtn=document.createElement("button");
  const dv=document.createElement("div");
  const dvTop=document.createElement("button")
  dv.appendChild(dvTop)
  dvTop.innerHTML=inner
  dvTop.onclick = () => 
    send(chanel,{"text":text,"index":idx,"verseIdx":0})
  for (let j=0; j<partList.length; j+=1){
    const b=document.createElement("button")
    b.onclick=()=>
      send(chanel,{"text":text,"index":idx,"verseIdx":j})
    b.innerText=partList[j]
    dv.appendChild(b)
    console.log(b)

  }
  dv.dataShow="none"
  subBtn.innerText="👁"
  subBtn.onclick=(event)=>{
    event.stopPropagation()
    dv.dataShow=dv.dataShow=="none"?"":"none"
    dv.style.display=dv.dataShow
  }
  dv.style.display="none"
  btn.appendChild(subBtn)
  cont.appendChild(dv)
}
function loadTalk(cont,btn,chanel,idx){
  const text=btn.data.text
  btn.searchData=text
  loadItem(cont, btn, chanel, idx, text, btn.data.parts)
}
function loadSong(cont,btn,chanel,idx){
  const text=btn.data.text
  btn.searchData=sanitize(btn.data.titles.join(""))+"¤"+sanitize(btn.data.verses.join(""))
  loadItem(cont, btn, chanel, idx, btn.data.titles.join(' | ') , btn.data.verses)
}
socket.on("songSelected", (data) =>{
//songidx,vidx
  var tmp
  var nx
  var prv
  document.querySelectorAll(".HLT").forEach(b=>b.classList.remove("HLT") );
  const SF=document.getElementById("SongScroll")
  SF.children[2*data['songidx']].classList.add("HLT")
  const vs=SF.children[2*data['songidx']].data.verses
  if (data['vidx']>=0 && data['vidx']<vs.length)
    SF.children[2*data['songidx']+1].children[data['vidx']+1].classList.add("HLT")
  /*if (data['vidx']>0)
    prv=vs[data['vidx']-1].split('\n')[0]
  else if (data['vidx']==0)
    prv="Dal elötti üres"
  else {
    if (data['songidx']==0){
      tmp=SF.children[SF.children.length-2].data.verses
    }else{
      tmp=SF.children[2*(data['songidx']-1)].data.verses
    }
    prv=tmp[tmp.length-1].split('\n')[0]
  }
  if (data['vidx']<vs.length-1)
    nx=vs[data['vidx']+1].split('\n')[0]
  else 
    nx="Dal utáni logó"
  document.querySelectorAll(".PrevNote").forEach(x=> x.innerText=prv)
  document.querySelectorAll(".NextNote").forEach(x=> x.innerText=nx)
*/})
socket.on('previews',d=>{
  document.querySelectorAll(".PrevNote").forEach(x=> x.innerText=d.prev)
  document.querySelectorAll(".ActNote").forEach(x=> x.innerText=d.act)
  document.querySelectorAll(".NextNote").forEach(x=> x.innerText=d.next)
})
socket.on("volume",v =>{
  document.getElementById("volume").value=v
})
socket.on("Auto",v =>{
  document.getElementById("autoplay").checked =v
})

socket.on("songOrder",data =>{
  const items = data
  const cont=document.getElementById("SongOrderScroll")
  cont.innerHTML=""

  for (let i=0; i<items.length; i++){
    const btn=document.createElement("button");
    btn.innerHTML = "<div>"+items[i].text+"</div>";
    btn.data = items[i]
    if (btn.data.kind=="song"){
      loadSong(cont,btn,"songOrderSet",i)
    }else if (btn.data.kind=="talk"){
      loadTalk(cont,btn,"songOrderSet",i)
    }
  }
})
socket.on("songs",songs =>{
  //loadData("songSet", songs, "SongScroll")
  const items = songs
  const cont=document.getElementById("SongScroll")
  cont.innerHTML=""

  for (let i=0; i<items.length; i++){
    const btn=document.createElement("button");
    btn.innerHTML = "<div>"+items[i].text+"</div>";
    btn.data = items[i]
    loadSong(cont,btn,"songSet",i )
  }
})

socket.on("music",data =>{
  loadData("musicSet", data, "MusicScroll")
})
socket.on("talks",talks =>{
  const items = talks
  const cont=document.getElementById("TalkScroll")
  cont.innerHTML=""

  for (let i=0; i<items.length; i++){
    const btn=document.createElement("button");
    btn.innerHTML = "<div>"+items[i].text+"</div>";
    btn.data = items[i]
    loadTalk(cont,btn,"songOrderSet",i)
  }
})
socket.on("template",data =>{
  //TODO
})
function filterBtns(input,buttons){
  buttons.forEach(btn=>{
    if (btn.data) {//Not the eyes
      btn.style.display= btn.searchData.includes(sanitize(input.value))?"":"none"
      if (""==btn.style.display)
        btn.nextSibling.style.display=btn.nextSibling.dataShow
      else
        btn.nextSibling.style.display="none"
    }
  })
}
function makeFilter(id){
  const SF=document.getElementById(id+"Filter")
  SF.addEventListener("input",()=>
    filterBtns(SF,document.querySelectorAll("#"+id+"Scroll button"))
  )
  filterBtns(SF,document.querySelectorAll("#"+id+"Scroll button"))
}
function selectMode(mode){
  document.querySelectorAll(".container").forEach(cont => cont.style.display = cont.id==mode+"Cont"?"":"none")
}
function selectSubMode(mode){
  document.querySelectorAll(".SubMode").forEach(cont=>cont.style.display=cont.id==mode?"":"none")
}

