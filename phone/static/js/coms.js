function sanitize(orig){
  return orig .toLowerCase()
              .normalize("NFD")
              .replace(/[\u0300-\u036f]/g, "")
              .replace(/[^a-z0-9]/g,"")
}

function send(chanel,msg){
  msg.sent_at=Date.now();
  fetch(chanel, {
  method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(msg)
  });
}
async function loadData(chanel,data,contID){
  const itemsC= await fetch(data)
  const items = await itemsC.json();
  const cont=document.getElementById(contID)
  cont.innerHTML=""

  for (let i=0; i<items.length; i++){
    const btn=document.createElement("button");
    btn.innerHTML = items[i].text;
    btn.onclick = () => 
      send(chanel,{title:items[i].title,index:i})
    cont.appendChild(btn);
  }

}

async function loadSongs(){
  return loadData("/sendSong","SongList", "SongScroll")
}
async function loadTalks(){
  return loadData("/sendTalk","TalkList", "TalkScroll")
}
async function loadMusic(){
  return loadData("/sendMusic","MusicList", "MusicScroll")
}
function filterBtns(input,buttons){
  buttons.forEach(btn=>{

    btn.style.display= sanitize(btn.textContent).includes(sanitize(input.value))?"":"none"
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

