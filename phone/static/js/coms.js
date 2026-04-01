// @ts-check
/** @type {typeof import("socket.io-client").io} */
const io = window.io;

/**
 * @param {string} orig
 */
function sanitize(orig){
  return orig .toLowerCase()
              .normalize("NFD")
              .replace(/[\u0300-\u036f]/g, "")
              .replace(/[^a-z0-9]/g,"")
}

/**
 * @param {string} chanel
 * @param {{ text?: any; indexes?: number[] | any[]; sent_at?: any; }} msg
 */
function send(chanel,msg){
  if (typeof(msg)=='string'){
    msg={'text':msg}
  }
  msg.sent_at=Date.now();
  console.log(msg)
  socket.emit(chanel, JSON.stringify(msg));
}

class ElementItem{
  /** @type {string} */ text 
  /** @type {string} */ kind 
  /** @type {string[]|null} */ titles 
  /** @type {string} */ basicSearchData 
  /** @type {string} */ detailedSearchData
  /** @type {string | null} */ music
  /** @type {ElementItem[] | null} */ parts
}

const socket = io();

/**
 * @param {HTMLElement} cont
 * @param {string} chanel
 * @param {any} idx
 * @param {ElementItem} data
 * @param {number[]} idxprefix
 * @param {null | string} msg
 */
function loadItem(cont,chanel,idx,data,idxprefix=[],msg=null){
  if (msg==null)
    msg=data.text
  const btn=document.createElement("button");
  // @ts-ignore
  btn.innerHTML = "<div>"+data.text.trim().replaceAll('\n', '<br/>')+"</div>";
  btn.dataset.kind=data.kind
  btn.dataset.detailedSearchData=sanitize(data.detailedSearchData)
  btn.dataset.basicSearchData=sanitize( data.basicSearchData)
  //!!!btn.searchData
  btn.onclick = () => 
    send(chanel,{"text":msg,"indexes":idxprefix.concat([idx])})
  btn.id="Item|"+chanel+"|"+ idxprefix.concat([idx])
  cont.appendChild(btn);
  const dv=document.createElement("div");
  let dvEmpty=true
  if (data.titles != null && data.titles?.length > 1){
    const dvTop=document.createElement("button")
    dv.appendChild(dvTop)
    dvTop.innerHTML=data.titles.join("|")
    dvTop.onclick = () => 
    send(chanel,{"text":msg,"indexes":[idx]})
    dvEmpty=false
  }
  if (data.parts!=null){
    for (let j=0; j<data.parts?.length; j+=1){
      dvEmpty=false
      loadItem(dv, chanel, j, data.parts[j],idxprefix.concat([idx]),msg)
      /*
      const b=document.createElement("button")
      b.id= 'Item|'+chanel+'|'+idx+';'+j
      b.onclick=()=>
        send(chanel,{"text":text,"indexes":[idx,j]})
      b.innerText=data.parts[j].text
      dv.appendChild(b)*/
    }
  }
  if (!dvEmpty){
    const subBtn=document.createElement("button");
    dv.dataset.show="none"
    subBtn.innerText="👁"
    subBtn.onclick=(event)=>{
      event.stopPropagation()
      dv.dataset.show=dv.dataset.show=="none"?"":"none"
      dv.style.display=dv.dataset.show
    }
    dv.style.display="none"
    cont.appendChild(dv)
    btn.appendChild(subBtn)
  }
}

/**
 * @param {{ name: string; infoDate: number; status: string; age: number; length: number; }} m
 */
function makeMediaDataStr(m){
  if (m.name=="-") return "0:0"
  console.log(m)
  var t
  if (m.infoDate>0 && m.status=="PLAYING"){
    t= -(m.infoDate-Date.now()/1000)
  }else{
    t=0
  }
  return Math.round(m.age+t)+":"+Math.round( m.length)
}

let musicInterval=-1

socket.on('previews',d=>{
  document.querySelectorAll(".PrevNote").forEach(x=> {if (x instanceof HTMLElement) x.innerText=d.prev})
  document.querySelectorAll(".ActNote").forEach(x=> {if (x instanceof HTMLElement)x.innerText=d.act})
  document.querySelectorAll(".NextNote").forEach(x=> {if (x instanceof HTMLElement)x.innerText=d.next})
  document.querySelectorAll(".MediaNameNote").forEach(x=> {if (x instanceof HTMLElement) x.innerText= d.media.name.split(/[/\\]/).pop() })
  const songMedia=d.media
  document.querySelectorAll(".MediaDataNote").forEach(x=> {if (x instanceof HTMLElement)x.innerText=makeMediaDataStr(d.media)})
  if ( musicInterval!=7){
    clearInterval(musicInterval)
  }
  if (d.media.status=="PLAYING")
  musicInterval= setInterval(() => {
      document.querySelectorAll(".MediaDataNote").forEach(x=> {if (x instanceof HTMLElement)x.innerText = makeMediaDataStr(songMedia)});
  }, 1000);

  document.querySelectorAll(".HLT").forEach(x=>x.classList.remove("HLT"))
  const tmp=document.getElementById("Item|"+d.mode+"Set|"+d.indexes[0])
  if (tmp)
    tmp.classList.add("HLT")
  const tmp2=d.indexes.length>1 && document.getElementById("Item|"+d.mode+"Set|"+d.indexes[0]+","+d.indexes[1])
  if (tmp2)
    tmp2.classList.add("HLT")
  
  
})
socket.on("volume",v =>{
  /** @type {HTMLInputElement} */
  // @ts-ignore
  const vctrl=document.getElementById("volume")
  vctrl.value=v
})
socket.on("Auto",v =>{
  // @ts-ignore
  document.getElementById("autoplay").checked =v
})

socket.on("songOrder",data =>{
  /** @type {ElementItem[]} */
  const items = data
  const cont=document.getElementById("SongOrderScroll")
  if (cont==null)
    return
  cont.innerHTML=""

  for (let i=0; i<items.length; i++){
    loadItem(cont, "songOrderSet", i, items[i])
  }
})
socket.on("songs",songs =>{
  /** @type {ElementItem[]} */
  const items = songs
  const cont=document.getElementById("SongScroll")
  if (cont==null) return
  cont.innerHTML=""

  for (let i=0; i<items.length; i++){
    loadItem(cont,"songSet",i ,items[i])
  }
})

socket.on("music",data =>{
  //TODO
})
socket.on("talks",talks =>{
  /** @type {ElementItem[]} */
  const items = talks
  const cont=document.getElementById("TalkScroll")
  if (cont ==null){
    return
  }
  cont.innerHTML=""

  for (let i=0; i<items.length; i++){
    loadItem(cont,"talkSet",i ,items[i])
  }
})
socket.on("template",data =>{
  //TODO
})
/**
 * @param {HTMLInputElement} input
 * @param {NodeListOf<HTMLElement>} buttons
 */
function filterBtns(input,buttons){
  buttons.forEach(btn=>{
    if (btn.dataset.detailedSearchData) {//Not the eyes
      btn.style.display= btn.dataset.detailedSearchData.includes(sanitize(input.value))?"":"none"
      /** @type {HTMLElement} */
      // @ts-ignore
      const nxt=btn.nextSibling
      if (nxt)
        if (""==btn.style.display)
          // @ts-ignore
          nxt.style.display=nxt.dataset.show
        else
          nxt.style.display="none"
    }
  })
}
/**
 * @param {string} id
 */
function makeFilter(id){
  /** @type {HTMLInputElement} */
  // @ts-ignore
  const SF=document.getElementById(id+"Filter")
  SF.addEventListener("input",()=>
    filterBtns(SF,document.querySelectorAll("#"+id+"Scroll button"))
  )
  filterBtns(SF,document.querySelectorAll("#"+id+"Scroll button"))
}
/**
 * @param {string} mode
 */
function selectMode(mode){
  /** @type {NodeListOf<HTMLElement>} */
  const elements=document.querySelectorAll(".container")
  elements.forEach(cont => cont.style.display = cont.id==mode+"Cont"?"":"none")
}
/**
 * @param {string} mode
 */
function selectSubMode(mode){
  /** @type {NodeListOf<HTMLElement>} */
  const elements=document.querySelectorAll(".SubMode")
  elements.forEach(cont=>cont.style.display=cont.id==mode?"":"none")
}

socket.on('ping', () => {
  console.log('ping')
})
/*
socket.on('disconnect', (reason) => {
    console.log("Connection lost:", reason);
    showAlertUser("You are offline. Trying to reconnect...");
});

// Triggered when the connection is successfully restored
socket.on('connect', () => {
    hideAlertUser();
    console.log("Connected to server!");
});

// Optional: Specific handling for manual reconnections
socket.on('reconnect_attempt', () => {
    console.log("Attempting to reconnect...");
});*/
