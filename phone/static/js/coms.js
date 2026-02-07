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
  console.log(msg)
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
    btn.innerHTML = items[i].text;
    btn.data = items[i].searchData
    btn.onclick = () => 
      send(chanel,{"text":items[i].text,"index":i})
    cont.appendChild(btn);
    if (btn.data!=btn.innerText){
      const subBtn=document.createElement("button");
      const dv=document.createElement("div");
      dv.innerText=btn.data
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
  }
}
socket.on("volume",v =>{
  document.getElementById("volume").value=v
})
socket.on("Auto",v =>{
  document.getElementById("autoplay").checked =v
})
socket.on("songs",songs =>{
  loadData("songSet", songs, "SongScroll")
})

socket.on("talks",data =>{
  loadData("talkSet", data, "TalkScroll")
})
socket.on("music",data =>{
  loadData("musicSet", data, "MusicScroll")
})
socket.on("template",data =>{
  //TODO
})
function filterBtns(input,buttons){
  buttons.forEach(btn=>{
    if (btn.data) {//Not the eyes
      btn.style.display= sanitize(btn.data).includes(sanitize(input.value))?"":"none"
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

