socket = io("https://localhost:1111")
const Topleftbutton = document.getElementById("topleft")
const Toprightbutton = document.getElementById("topright")
const Bottomleftbutton = document.getElementById("bottomleft")
const Bottomrightbutton = document.getElementById("bottomright")
const canvascontainer = document.getElementById("canvascontainer")
const waiting = document.getElementById("waiting")
var canvashidden = false

const Items = []
var items = ["null item", "Capsule", "Super Capsule", "Mega Capsule", "Ultra Capsule", "Perfected Capsule",
             "Heal Spray", "Super Heal Spray", "Mega Heal Spray", "Ultra Heal Spray", "Senzu Bean"]
var descriptions = ["null description", "The original capsule design, had lots of flaws", "An upgrade from the original capsule, bug fix: Fixed error with distorting time",
                    "The Mega Capsule was designed to store very large things including powerlevels", "The Mega capsules big brother the Ultra Capsule",
                    "This capsule is perfection, hard to come by so make proper use of it", "The heal spray heals the smallest of wounds: 50hp", "The super heal spray can heal any super hero: 100hp",
                    "Intended use: God: 200hp", "Ultra heal spray can heal any one wound: 400hp", "Gods Gift: 1000hp"]
class Item {
    constructor(id) {
        this.id = id
        this.type = (Math.floor((this.id-1) / 5)) + 1
        this.subid = (this.id - 1)%5
        this.itemname = items[this.id]
        this.itemdescription = descriptions[this.id]
    }

    GetAmount(Amount) {
        this.Amount = Amount
    }
}

function startbuttons(){
    Topleftbutton.innerHTML = "Team"
    Toprightbutton.innerHTML = "Moves"
    Bottomleftbutton.innerHTML = "Bag"
    Bottomrightbutton.innerHTML = "Run"
    Topleftbutton.style.display = "block"
    Toprightbutton.style.display = "block"
    Bottomleftbutton.style.display = "block"
    Bottomrightbutton.style.display = "block"
    waiting.style.display = "none"
    waiting.innerHTML = " Waiting for Opponents Move "
    Toprightbutton.onclick = Domoves
    Topleftbutton.onclick = DisplayTeam
    Bottomrightbutton.onclick = Run
    Bottomleftbutton.onclick = function(){
        socket.emit("Bag")
    }
}

function Domoves(event){
    if(canvas.style.display=="none"){
        canvas.style.display="block"
        let tbl = document.getElementById("contentstable")
        tbl.remove()
    }
    let Moves = player.getcurrentmoves()
    Topleftbutton.innerHTML = Moves[0]
    Toprightbutton.innerHTML = Moves[1]
    Bottomleftbutton.innerHTML = Moves[2]
    Bottomrightbutton.innerHTML = Moves[3]
    Topleftbutton.onclick = Domove1
    Toprightbutton.onclick = Domove2
    Bottomleftbutton.onclick = Domove3
    Bottomrightbutton.onclick = Domove4
}
function hideandwait(){
    Topleftbutton.style.display = "none"
    Toprightbutton.style.display = "none"
    Bottomleftbutton.style.display = "none"
    Bottomrightbutton.style.display = "none"
    waiting.style.display = "flex"
}
function Domove1(){
    player.selectmove1()
    if(type==2){
        hideandwait()
    }
}
function Domove2(){
    player.selectmove2()
    if(type==2){
        hideandwait()
    }
}
function Domove3(){
    player.selectmove3()
    if(type==2){
        hideandwait()
    }
}
function Domove4(){
    player.selectmove4()
    if(type==2){
        hideandwait()
    }
}
function Run(){
    if(type==0){
        socket.emit("GoBack")
    }else if(type==2){
        socket.emit("runaway")
        socket.emit("GoBack")
    }
}
socket.on("ToGame", (message) =>{
    playerid = message.PID
    location.href = "https://localhost:1111/Game?data="+ playerid
  })

function Displayitems(){
    if(canvashidden == false){
        canvas.classList.remove("item")
        canvas.classList.add("shrink")
        let table = document.createElement("table")
        table.id = "contentstable"
        let thead = document.createElement("thead")
        let headrow = document.createElement("tr")
        let headcell1 = document.createElement("td")
        let headcell2 = document.createElement("td")
        let headcell3 = document.createElement("td")
        let headcell4 = document.createElement("td")
        headcell1.innerHTML = "Name: "
        headcell2.innerHTML = "Description: "
        headcell3.innerHTML = "Quantity: "
        headcell4.innerHTML = "Select: "
        headrow.appendChild(headcell1)
        headrow.appendChild(headcell2)
        headrow.appendChild(headcell3)
        headrow.appendChild(headcell4)
        thead.appendChild(headrow)
        table.appendChild(thead)
        let tbody = document.createElement("tbody")
        for(let i = 0; i<Items.length;i++){
            let item = Items[i]
            if (item!=null){
                let row = document.createElement("tr")
                let cell1 = document.createElement("td")
                let cell2 = document.createElement("td")
                let cell3 = document.createElement("td")
                let cell4 = document.createElement("td")
                cell1.innerHTML = item.itemname
                row.appendChild(cell1)
                cell2.innerHTML = item.itemdescription
                row.appendChild(cell2)
                cell3.innerHTML = item.Amount
                row.appendChild(cell3)
                let button = document.createElement("button")
                button.innerHTML = "Select"
                button.onclick = function(){
                    if(type!=0&&item.type==1){
                        button.innerHTML = "Cannot use"
                    }else if (item.type==1){
                        let itemid = item.type*(item.subid+1)
                        socket.emit("itemused", itemid)
                        let rand
                        player.Character.move = nonemove
                        if(item.subid==0){
                            rand = Math.floor(Math.random()*60)
                            player.Character.Move= nonemove
                            opponent.choosemove()
                        }else if(item.subid==1){
                            rand = Math.floor(Math.random()*70)
                            player.Character.Move= nonemove
                            opponent.choosemove()
                        }else if(item.subid==2){
                            rand = Math.floor(Math.random()*80)
                            player.Character.Move= nonemove
                            opponent.choosemove()
                        }else if(item.subid==3){
                            rand = Math.floor(Math.random()*100)
                            player.Character.Move= nonemove
                            opponent.choosemove()
                        }else if(item.subid==4){
                            rand = 100
                        }
                        if(rand>=50){
                            socket.emit("caughtopp")
                            background.image.src = "static/Assets/Win.png"
                            player.removeself()
                            opponent.removeself()
                            background.update()
                            document.addEventListener("keydown", function(){
                                socket.emit("offlinewin")
                                Goback()
                            })
                        }
                    }
                    if(item.type==2){
                        let itemid = (item.type-1)*5+(item.subid+1)
                        socket.emit("itemused", itemid)
                        player.Character.move = nonemove
                        if(type==2){
                            if(item.subid==0){
                                socket.emit("healused", 50)
                                socket.emit("MoveChosen", nonemove)
                                hideandwait()
                            }else if(item.subid==1){
                                socket.emit("healused", 100)
                                socket.emit("MoveChosen", nonemove)
                                hideandwait()
                            }else if(item.subid==2){
                                socket.emit("healused", 200)
                                socket.emit("MoveChosen", nonemove)
                                hideandwait()
                            }else if(item.subid==3){
                                socket.emit("healused", 400)
                                socket.emit("MoveChosen", nonemove)
                                hideandwait()
                            }else if(item.subid==4){
                                socket.emit("healused", 1000)
                                socket.emit("MoveChosen", nonemove)
                                hideandwait()
                            }
                        } else{
                            if(item.subid==0){
                                player.Character.Heal(50)
                            }else if(item.subid==1){
                                player.Character.Heal(100)
                            }else if(item.subid==2){
                                player.Character.Heal(200)
                            }else if(item.subid==3){
                                player.Character.Heal(400)
                            }else if(item.subid==4){
                                player.Character.Heal(1000)
                            }
                        }
                    }
                    table.classList.remove("item")
                    table.classList.add("shrink")
                    setTimeout(function(){
                        canvas.classList.remove("shrink")
                        canvas.classList.add("item")
                        table.remove()
                    }, 600)
                    canvashidden = false
                    Items.splice(0,Items.length)
                }
                cell4.appendChild(button)
                row.appendChild(cell4)
                tbody.appendChild(row)
            }
        }
        let opacity = 0
        table.style.opacity = "0"
        setTimeout(function(){
            canvashidden = true
            table.appendChild(tbody)
            canvascontainer.appendChild(table)
            setInterval(function(){
                table.style.opacity = String(opacity+0.1)
                opacity= opacity+ 0.1
            }, 35)
        }, 600)
    }else{
        let tbl = document.getElementById("contentstable")
        tbl.classList.remove("item")
        tbl.classList.add("shrink")
        setTimeout(function(){
            canvas.classList.remove("shrink")
            canvas.classList.add("item")
            tbl.remove()
        }, 600)
        canvashidden = false
    }
}
function DisplayTeam(){
    if(canvashidden == false){
        canvas.classList.remove("item")
        canvas.classList.add("shrink")
        var Characters = player.getCharacters()
        let table = document.createElement("table")
        table.id = "contentstable"
        let thead = document.createElement("thead")
        let headrow = document.createElement("tr")
        let headcell1 = document.createElement("td")
        let headcell2 = document.createElement("td")
        let headcell3 = document.createElement("td")
        let headcell4 = document.createElement("td")
        headcell1.innerHTML = "Character: "
        headcell2.innerHTML = "Image: "
        headcell3.innerHTML = "Hp: "
        headcell4.innerHTML = "Select: "
        headrow.appendChild(headcell1)
        headrow.appendChild(headcell2)
        headrow.appendChild(headcell3)
        headrow.appendChild(headcell4)
        thead.appendChild(headrow)
        table.appendChild(thead)
        let tbody = document.createElement("tbody")
        for(let i = 0; i<Characters.length;i++){
            let Character = Characters[i]
            if (Character!=null){
                let row = document.createElement("tr")
                let cell1 = document.createElement("td")
                let cell2 = document.createElement("td")
                let cell3 = document.createElement("td")
                let cell4 = document.createElement("td")
                cell1.innerHTML = Character.name
                row.appendChild(cell1)
                let img = document.createElement("img")
                img.src = "static/Assets/"+Character.name+".png"
                cell2.appendChild(img)
                row.appendChild(cell2)
                cell3.innerHTML = Character.hp
                row.appendChild(cell3)
                let button = document.createElement("button")
                button.innerHTML = "Select"
                button.onclick = function(){
                    player.SwitchCharacter(i)
                    table.classList.remove("item")
                    table.classList.add("shrink")
                    setTimeout(function(){
                        canvas.classList.remove("shrink")
                        canvas.classList.add("item")
                        table.remove()
                    }, 600)
                    canvashidden = false
                }
                cell4.appendChild(button)
                row.appendChild(cell4)
                tbody.appendChild(row)
            }
        }
        let opacity = 0
        table.style.opacity = "0"
        setTimeout(function(){
            canvashidden = true
            table.appendChild(tbody)
            canvascontainer.appendChild(table)
            setInterval(function(){
                table.style.opacity = String(opacity+0.1)
                opacity= opacity+ 0.1
            }, 35)
        }, 600)
    } else{
        let tbl = document.getElementById("contentstable")
        tbl.classList.remove("item")
        tbl.classList.add("shrink")
        setTimeout(function(){
            canvas.classList.remove("shrink")
            canvas.classList.add("item")
            tbl.remove()
        }, 600)
        canvashidden = false
    }
}
startbuttons()