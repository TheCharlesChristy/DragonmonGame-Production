var Names = []
var ids
var Levels = []
var CurrentHps = []
var FullHps = []
var Urls = []
var States = []
socket.on("Namesandids", (data) => {
    let Namesdict = data.Names
    ids = data.ids
    Names = Object.values(Namesdict)
})
socket.on("Levels", (data) => {
    Levels = Object.values(data)
})
socket.on("CurrentHps", (data) => {
    CurrentHps = Object.values(data)
})
socket.on("FullHp", (data) => {
    FullHps = Object.values(data)
})
socket.on("Urls", (data) => {
    Urls = Object.values(data)
})
socket.on("States", (data) => {
    States = Object.values(data)
    doTeamTable()
})

function doTeamTable() {
    oldtable = document.getElementById("Itemtable")
    const table = document.createElement('table');
    const tbody = document.createElement('tbody');
    table.style.width = "100%"
    tbody.classList.add("itemtablebody")
    table.id = "Itemtable"
    for (let y = 0; y < Names.length+1; y++) {
      const row = document.createElement('tr');
      row.classList.add("itemrow")
      for (let x = 0; x <= 4; x++) {
        const cell = document.createElement('td');
        cell.classList.add("teamcell")
        if (y==0){
            if (x==0){
                text = document.createElement("p")
                text.classList.add("tabletext")
                text.innerHTML = "Name"
                cell.appendChild(text)
            }
            if (x==1){
                text = document.createElement("p")
                text.classList.add("tabletext")
                text.innerHTML = "Level"
                cell.appendChild(text)
            }
            if (x==2){
                text = document.createElement("p")
                text.classList.add("tabletext")
                text.innerHTML = "Hp"
                cell.appendChild(text)
            }
            if (x==3){
                text = document.createElement("p")
                text.classList.add("tabletext")
                text.innerHTML = "Image"
                cell.appendChild(text)
            }
            if (x==4){
                text = document.createElement("p")
                text.classList.add("tabletext")
                text.innerHTML = "Active"
                cell.appendChild(text)
            }
        }
        else {
            if (x==0){
                text = document.createElement("p")
                text.classList.add("tabletext")
                text.id = "Charname"
                text.innerHTML = Names[y-1]
                cell.appendChild(text) 
            }
            if (x==1){
                text = document.createElement("p")
                text.classList.add("tabletext")
                text.innerHTML = Levels[y-1]
                cell.appendChild(text) 
            }
            if (x==2){
                text = document.createElement("p")
                text.classList.add("tabletext")
                part1 = Math.floor(CurrentHps[y-1]).toString()
                half2 = FullHps[y-1].toString()
                half1 = part1.concat("/")
                full = half1.concat(half2)
                text.innerHTML = full
                cell.appendChild(text)
            }
            if (x==3){
                img = document.createElement("img")
                url = Urls[y-1]
                img.src = url
                cell.appendChild(img)
            }
            if (x==4){
                let button = document.createElement("button")
                const state = States[y-1]
                button.innerHTML = state
                button.dataset.character = ids[y-1]
                button.addEventListener("click", function(){
                    if (state == "Active"){
                        socket.emit("RemoveTeamMember", button.dataset.character)
                    }else{
                        socket.emit("AddTeamMember", button.dataset.character)
                    }
                })
                cell.appendChild(button)
            }
        }

        row.appendChild(cell)
      }
      tbody.appendChild(row);
    }
    table.appendChild(tbody);
    try{
        canvas.classList.remove("item")
        canvas.classList.add("shrink")
        table.style.position = "absolute"
        table.style.top = "1400px"
        pos = 1400
        setTimeout(function(){
            canvas.parentNode.replaceChild(table, canvas)
        }, 600);
        let slider = setInterval(function(){
            pos = pos-5
            table.style.top = String(pos)+"px"
            if(pos<3){
                clearInterval(slider)
            }
        }, 1);
        if(pos<3){
            clearInterval(slider)
        }
    }catch{
        oldtable.parentNode.replaceChild(table, oldtable)
        //Case of bag=open

    }
  }