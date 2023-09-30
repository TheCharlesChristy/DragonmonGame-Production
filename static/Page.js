const socket = io('https://localhost:1111')
var start = false
var Game
var player
var background
var NPCGroup = []
var FriendGroup = []
const body = document.getElementById("body")
socket.on('connect',function(){ 
    socket.emit("Finalise", username)
})

socket.on("Activecharacters", (message) => {
    let oldcontainer = document.getElementById("leftcontainer")
    oldcontainer.remove()
    let container = document.createElement("div")
    container.id = "leftcontainer"
    container.classList.add("leftcontainer")
    body.appendChild(container)
    let names = message["Characters"]
    let urls = message["Urls"]
    let levels = message["Levels"]
    let table = document.createElement("table")
    for(let y = 0;y<names.length*2;y++){
        let row = document.createElement("tr")
        let cell = document.createElement("td")
        if (y%2==0){
            let tblimg = document.createElement("img")
            let url = urls[y/2]
            tblimg.src = url
            cell.appendChild(tblimg)
            cell.style.justifyContent = "center"
            cell.style.display = "flex"
        }else{
            let text = document.createElement("p")
            text.innerHTML = names[Math.floor(y/2)]
            text.style.textAlign = "center"
            cell.appendChild(text)
            let text2 = document.createElement("p")
            text2.innerHTML = "Level: "+levels[Math.floor(y/2)]
            text2.style.textAlign = "center"
            cell.appendChild(text2)
        }
        row.appendChild(cell)
        table.appendChild(row)
        container.appendChild(table)
    }
})
socket.on("mapdata", (message) => {
    Game = message["data"]
    let xpos = message["xpos"]
    let ypos = message["ypos"]
    let fnames = message["map"]
    background = new Background(fnames[0], fnames[1])
    player = new Player({
        x:xpos*12,
        y:ypos*12
    })
    start = true
})
socket.on("NPCS", (message) => {
    let ids = message["ids"]
    let xpositions = message["xposs"]
    let ypositions = message["yposs"]
    let lookings = message["lookings"]
    let Beatenids = message["beaten"]
    for (let i = 0;i<ids.length;i++){
        let Active
        if (Beatenids.includes(ids[i])){
            Active = false
        }else{
            Active = true
        }
        let position = {
            x:xpositions[i]*12,
            y:ypositions[i]*12
        }
        let newAI = new NPC(ids[i], position, lookings[i], Active)
    }
})
socket.on("Friendpos", (message) => {
    let account = message["account"]
    let xposition = message["xpos"]
    let yposition = message["ypos"]
    let position = {
        x:xposition,
        y:yposition
    }
    let friend = new Friend(account, position)
})
socket.on("UpdateFriendpos", (message) => {
    let target = message["account"]
    let nxtmove = message["nextmove"]
    for (let i=0;i<FriendGroup.length;i++){
        let current = FriendGroup[i]
        if (current.name==target){
            current.movestodo.push(nxtmove)
        }
    }
})


socket.on("battlerequestdata", (message) => {
    let container = document.getElementById("rightcontainer")
    let names = message["names"]
    if (document.getElementById("battlerequests")!=null){
        document.getElementById("battlerequests").remove()
    }
    let table = document.createElement("table")
    table.id = "battlerequests"
    table.style.margin = "0px"
    table.style.padding = "0px"
    table.style.display = "flex"
    table.style.flexDirection = "column"
    table.style.justifyContent = "space-evenly"
    table.style.alignItems = "center"
    for(let y = 0;y<names.length;y++){
        let row = document.createElement("tr")
        row.style.display = "flex"
        row.style.justifyContent = "space-between"
        let r1 = document.createElement("tr")
        let cell1 = document.createElement("td")
        let text = document.createElement("p")
        text.innerHTML = names[y]
        text.style.fontSize = "15px"
        cell1.appendChild(text)
        cell1.style.width = "100%"
        cell1.style.display = "flex"
        cell1.style.justifyContent = "center"
        r1.appendChild(cell1)
        r1.style.width = "100%"
        table.appendChild(r1)
        let cell2 = document.createElement("td")
        let btn = document.createElement("button")
        btn.style.border = "2px black"
        btn.style.borderRadius = "5px"
        btn.style.width = "100%"
        btn.style.backgroundColor = "lightblue"
        btn.innerHTML = "Battle"
        btn.style.fontSize = "8px"
        btn.style.padding = "0px"
        btn.onmouseover = function(){
            btn.style.backgroundColor = "cornflowerblue"
        }
        btn.onmouseleave = function(){
            btn.style.backgroundColor = "lightblue"
        }
        btn.onclick = function(){
            socket.emit("Acceptbattle", text.innerHTML)
        }
        cell2.appendChild(btn)
        cell2.style.width = "50%"
        cell2.style.display = "flex"
        cell2.style.justifyContent = "center"
        row.appendChild(cell2)
        let cell3 = document.createElement("td")
        let btn2 = document.createElement("button")
        btn2.style.border = "2px black"
        btn2.style.borderRadius = "5px"
        btn2.style.backgroundColor = "red"
        btn2.style.width = "100%"
        btn2.innerHTML = "Decline"
        btn2.style.fontSize = "8px"
        btn2.style.padding = "0px"
        btn2.onmouseover = function(){
            btn2.style.backgroundColor = "darkred"
        }
        btn2.onmouseleave = function(){
            btn2.style.backgroundColor = "red"
        }
        btn2.onclick = function(){
            socket.emit("Declinebattle", text.innerHTML)
            row.remove()
            r1.remove()
        }
        cell3.appendChild(btn2)
        cell3.style.width = "50%"
        cell3.style.display = "flex"
        cell3.style.justifyContent = "center"
        row.appendChild(cell3)
        row.style.width = "100%"
        row.style.height = "50px"
        table.appendChild(row)
    }
    container.appendChild(table)
})

function Friends() {
    b.classList.remove("item")
    b.classList.add("shrink")
    setTimeout(() => {
        socket.emit("Friends")
        socket.on('Friends', function(Token) {
            const token = Token.data
            location.href = "https://localhost:1111/Friends?token="+token
        })
    }, 500)
  }

function Bag() {
    let container = document.getElementById("maincontainer")
    currentgamebutton = document.getElementById("Game")
    if (currentgamebutton != null){
        currentgamebutton.click()
    }
    container.style.overflowY = "scroll"
    let oldbutton = document.getElementById("Bag")
    let button = document.createElement("button")
    button.innerHTML = "Game"
    button.classList.add("button1")
    button.id = "Game"
    button.addEventListener("click", function(){
        let container = document.getElementById("maincontainer")
        container.style.overflowY = "hidden"
        table = document.getElementById("Itemtable")
        table.classList.remove("item")
        table.classList.add("shrink")
        setTimeout(() => {
            table.parentNode.replaceChild(canvas, table);
            canvas.classList.remove("shrink")
            canvas.classList.add("start")
        }, 1000);
        setTimeout(() => {
            canvas.classList.remove("start")
            canvas.classList.add("item")
        }, 1500);
        setTimeout(() => {
            console.log("timer")
        }, 1000);
        let oldbutton = document.getElementById("Game")
        let button = document.createElement("button")
        button.innerHTML = "Bag"
        button.classList.add("button1")
        button.id = "Bag"
        button.onclick = Bag
        oldbutton.parentNode.replaceChild(button, oldbutton)

    })
    oldbutton.parentNode.replaceChild(button, oldbutton)
    Items.splice(0, Items.length)
    socket.emit("Bag")
}
function Team() {
    let container = document.getElementById("maincontainer")
    currentgamebutton = document.getElementById("Game")
    if (currentgamebutton != null){
        currentgamebutton.click()
    }
    container.style.overflowY = "scroll"
    let oldbutton = document.getElementById("Team")
    let button = document.createElement("button")
    button.innerHTML = "Game"
    button.classList.add("button1")
    button.id = "Game"
    button.addEventListener("click", function(){
        let container = document.getElementById("maincontainer")
        container.style.overflowY = "hidden"
        table = document.getElementById("Itemtable")
        table.classList.remove("item")
        table.classList.add("shrink")
        setTimeout(() => {
            table.parentNode.replaceChild(canvas, table);
            canvas.classList.remove("shrink")
            canvas.classList.add("start")
        }, 1000);
        setTimeout(() => {
            canvas.classList.remove("start")
            canvas.classList.add("item")
        }, 1500);
        setTimeout(() => {
            console.log("timer")
        }, 1000);
        let oldbutton = document.getElementById("Game")
        let button = document.createElement("button")
        button.innerHTML = "Team"
        container.style.overflowY = "hidden"
        button.classList.add("button1")
        button.id = "Team"
        button.onclick = Team
        oldbutton.parentNode.replaceChild(button, oldbutton)
    })
    oldbutton.parentNode.replaceChild(button, oldbutton)
    Items.splice(0, Items.length)
    socket.emit("Team")
}
function Messages() {
    b.classList.remove("item")
    b.classList.add("shrink")
    setTimeout(() => {
        socket.emit("Redirecting")
        socket.on("Redirectconfirmed", (message) => {
            let Token = message.token
            location.href = "https://localhost:1111/Messages?token="+Token
        })
    }, 500)
}

socket.on("battle", (message) => {
    playerid = message["pid"]
    b.classList.remove("item")
    b.classList.add("shrink")
    setTimeout(() => {
        location.href = "https://localhost:1111/Battle?pid="+playerid
    }, 500)
})
socket.on("Confirmbattle", (message) =>{
    battleid = message["battleid"]
    socket.emit("Dolivebattle", battleid)
})