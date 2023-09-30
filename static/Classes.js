usernameelement  = document.getElementById("username")
username = usernameelement.innerHTML.replace("Logged in as ","")
const canvascontainer = document.getElementById("maincontainer")
const canvas = document.querySelector("canvas")
const c = canvas.getContext("2d")
canvas.width = 900
canvas.height = 600

class Background {
    constructor(imageSrc, Topimagesrc) {
        this.position = {
            x:0,
            y:0
        }
        this.width = 900
        this.height = 600
        this.centre = {
            x: this.width/2,
            y: this.height/2
        }
        this.image = new Image()
        this.image.src = imageSrc
        this.topimage = new Image()
        this.topimage.src = Topimagesrc
    }

    draw() {
        c.drawImage(this.image, this.position.x, this.position.y)
    }
    drawtop() {
        c.drawImage(this.topimage, this.position.x, this.position.y)
    }
}


class Player{
    constructor(position){
        this.width = 24
        this.height = 24
        this.position = {
            x: position.x,
            y: position.y
        }
        this.lastposition = {
            x:0,
            y:0
        }
        this.runs = {
            w:0,
            a:0,
            s:0,
            d:0
        }
        this.moving = false
        this.locked = false
        this.ingrass = false
        this.actualtile1 = Game[this.position.y/12][this.position.x/12]
        this.actualtile2 = Game[(this.position.y/12)][(this.position.x/12)+1]
        this.actualtile3 = Game[(this.position.y/12)+1][(this.position.x/12)]
        this.actualtile4 = Game[(this.position.y/12)+1][(this.position.x/12)+1]
        this.tile1tochangex = this.position.x/12
        this.tile1tochangey = this.position.y/12
        this.tile2tochangex = this.position.x/12
        this.tile2tochangey = this.position.y/12
        this.GamePosition()
        this.upimage = new Image()
        this.upimage.src = "static/Assets/playerUp.png"
        this.leftimage = new Image()
        this.leftimage.src = "static/Assets/playerLeft.png"
        this.downimage = new Image()
        this.downimage.src = "static/Assets/playerDown.png"
        this.rightimage = new Image()
        this.rightimage.src = "static/Assets/playerRight.png"
        this.image = new Image()
        this.image = this.downimage
    }
    GamePosition(){
        let x = this.position.x/12
        let y = this.position.y/12
        Game[y][x] = this
        Game[y][x+1] = this
        Game[y+1][x] = this
        Game[y+1][x+1] = this
        let coordinates = [y,x]
        return coordinates
    }
    draw() {
        //drawImage(image, sourcex, sourcey, sourceWidth, sourceHeight, destinationx, destinationy, destinationWidth, destinationHeight)
        let sx
        if (this.runs.w != 0){
            sx = (this.runs.w%4)*24
        }else
        if (this.runs.a != 0){
            sx = (this.runs.a%4)*24
        }else
        if (this.runs.s != 0){
            sx = (this.runs.s%4)*24
        }else
        if (this.runs.d != 0){
            sx = (this.runs.d%4)*24
        }else{
            sx = 0
        }

        c.drawImage(this.image, sx, 0, 24, 24, this.position.x, this.position.y, 24, 24)
    }
    update() {
        this.donextmove()

        this.draw()
    }
    detectobstruction(direction){
        let currentcoords = this.GamePosition()
        let x = currentcoords[1]
        let y = currentcoords[0]
        let target1
        let target2
        if (direction=="up"){
            target1 = Game[y-1][x]
            target2 = Game[y-1][x+1]
        }else if (direction=="left"){
            target1 = Game[y][x-1]
            target2 = Game[y+1][x-1]
        }
        else if (direction=="down"){
            target1 = Game[y+2][x]
            target2 = Game[y+2][x+1]
        }else{
            target1 = Game[y][x+2]
            target2 = Game[y+1][x+2] 
        }
        let check1
        let check2
        try{
            check1 = target1%2
            check2 = target2%2
        }catch{
            return true
        }
        if (check1+check2==0){
            if (direction=="up"){
                this.actualtile3 = this.actualtile1
                this.actualtile4 = this.actualtile2
                this.actualtile1 = target1
                this.actualtile2 = target2
                if(target1==1026||target2==1026||this.actualtile3==1026||this.actualtile4==1026){
                    this.ingrass=true
                }else{
                    this.ingrass=false
                }
                this.tiletochange1 = this.actualtile3
                this.tile1tochangex = x
                this.tile1tochangey = y+1
                this.tile2tochangex = x+1
                this.tile2tochangey = y+1
                this.tiletochange2 = this.actualtile4
            }else if(direction=="left"){
                this.actualtile2 = this.actualtile1
                this.actualtile4 = this.actualtile3
                this.actualtile1 = target1
                this.actualtile3 = target2
                if(target1==1026||target2==1026||this.actualtile2==1026||this.actualtile4==1026){
                    this.ingrass=true
                }else{
                    this.ingrass=false
                }
                this.tile1tochangex = x+1
                this.tile1tochangey = y
                this.tile2tochangex = x+1
                this.tile2tochangey = y+1
                this.tiletochange1 = this.actualtile2
                this.tiletochange2 = this.actualtile4
            }
            else if(direction=="down"){
                this.actualtile1 = this.actualtile3
                this.actualtile2 = this.actualtile4
                this.actualtile3 = target1
                this.actualtile4 = target2
                if(target1==1026||target2==1026||this.actualtile1==1026||this.actualtile2==1026){
                    this.ingrass=true
                }else{
                    this.ingrass=false
                }
                this.tile1tochangex = x
                this.tile1tochangey = y
                this.tile2tochangex = x+1
                this.tile2tochangey = y
                this.tiletochange1 = this.actualtile1
                this.tiletochange2 = this.actualtile2
            }else{
                this.actualtile1 = this.actualtile2
                this.actualtile3 = this.actualtile4
                this.actualtile2 = target1
                this.actualtile4 = target2
                if(target1==1026||target2==1026||this.actualtile1==1026||this.actualtile3==1026){
                    this.ingrass=true
                }else{
                    this.ingrass=false
                }
                this.tile1tochangex = x
                this.tile1tochangey = y
                this.tile2tochangex = x
                this.tile2tochangey = y+1
                this.tiletochange1 = this.actualtile1
                this.tiletochange2 = this.actualtile3
            }
            return false
        }else{
            return true
        }
    }
    donextmove(){
        if (keysdown.w&&this.runs.w==0&&!this.moving&&this.position.y>0){
            if(this.detectobstruction("up")==false&&this.locked==false){
                this.image = this.upimage
                socket.emit("MovePlayer", 1)
                this.lastposition = {
                    x:this.position.x,
                    y:this.position.y
                }
                this.runs.w = 4
                this.moving = true
            }
        }else if (keysdown.a&&this.runs.a==0&&!this.moving&&this.position.x>0){
            if(this.detectobstruction("left")==false&&this.locked==false){
                this.image = this.leftimage
                socket.emit("MovePlayer", 2)
                this.lastposition = {
                    x:this.position.x,
                    y:this.position.y
                }
                this.runs.a = 4
                this.moving = true
            }
        }else if (keysdown.s&&this.runs.s==0&&!this.moving&&this.position.y<576){
            if(this.detectobstruction("down")==false&&this.locked==false){
                this.image = this.downimage
                socket.emit("MovePlayer", 3)
                this.lastposition = {
                    x:this.position.x,
                    y:this.position.y
                }
                this.runs.s = 4
                this.moving = true
            }
        }else if (keysdown.d&&this.runs.d==0&&!this.moving&&this.position.x<876){
            if(this.detectobstruction("right")==false&&this.locked==false){
                this.image = this.rightimage
                socket.emit("MovePlayer", 4)
                this.lastposition = {
                    x:this.position.x,
                    y:this.position.y
                }
                this.runs.d = 4
                this.moving = true
            }
        }
        if(this.runs.w!=0){
            this.runs.w-=1
            this.position.y-=3
            if(this.ingrass&&this.runs.w==0){
                this.runodds()
            }
        }
        if(this.runs.a!=0){
            this.runs.a-=1
            this.position.x-=3
            if(this.ingrass&&this.runs.a==0){
                this.runodds()
            }
        }
        if(this.runs.s!=0){
            this.runs.s-=1
            this.position.y+=3
            if(this.ingrass&&this.runs.s==0){
                this.runodds()
            }
        }
        if(this.runs.d!=0){
            this.runs.d-=1
            this.position.x+=3
            if(this.ingrass&&this.runs.d==0){
                this.runodds()
            }
        }
        if (this.runs.w==0&&this.runs.a==0&&this.runs.s==0&&this.runs.d==0){
            this.moving = false
            Game[this.tile1tochangey][this.tile1tochangex] = this.tiletochange1
            Game[this.tile2tochangey][this.tile2tochangex] = this.tiletochange2
            this.GamePosition()
        }
    }
    runodds(){
        let randomnumber = Math.random()
        if (randomnumber<0.05){
            this.locked=true
            socket.emit("Grassbattle")
        }
    }
}

class Friend{
    constructor(name, position){
        this.name = name
        this.uid = Math.random()
        this.position = {"x":position.x*12, "y":position.y*12}
        this.movestodo = []
        this.sy = 0
        this.nextmove = 0
        this.runs = 0
        this.image = new Image()
        this.isbattlebox = false
        this.image.src = "static/Assets/Friend.png"
        FriendGroup.push(this)
    }
    doclick(){
        if(document.getElementById(String(this.uid))==null){
            let container = document.createElement("div")
            container.id = String(this.uid)
            container.style.position = "absolute"
            container.style.left = String(this.position.x+40) + "px"
            container.style.shape = String(this.position.x+40) + "px"
            container.style.top = String(this.position.y-50) + "px"
            container.style.height = "40px"
            container.style.width = "100px"
            container.style.display = "flex"
            container.style.justifyContent = "center"
            container.style.background = "aliceblue"
            container.style.fontSize = "10px"
            container.style.border = "solid black"
            container.style.borderRadius = "10px"
            container.style.borderWidth = "2px"
            let text = document.createElement("p")
            text.style.position = "absolute"
            text.style.top = "0px"
            text.style.margin = "0px"
            text.style.color = "#000000"
            text.innerHTML = this.name
            container.appendChild(text)
            let btn = document.createElement("button")
            btn.innerHTML = "Battle"
            btn.style.position = "absolute"
            btn.style.fontSize = "inherit"
            btn.style.bottom = "0px"
            btn.style.width = "90px"
            btn.style.backgroundColor = "lightblue"
            btn.style.borderRadius = "5px"
            btn.style.borderWidth = "1px"
            btn.style.padding = "0px"
            btn.onmouseover = function(){
                btn.style.backgroundColor = "cornflowerblue"
            }
            btn.onmouseleave = function(){
                btn.style.backgroundColor = "lightblue"
            }
            btn.onclick = function(){
                if(btn.innerHTML!="Sent"){
                    socket.emit("sendbattlerequest", text.innerHTML)
                    btn.innerHTML = "Sent"
                }
            }
            container.appendChild(btn)
            let exit = document.createElement("button")
            exit.innerHTML = "x"
            exit.style.position = "absolute"
            exit.style.fontSize = "10px"
            exit.style.top = "0px"
            exit.style.right = "5px"
            exit.style.width = "5px"
            exit.style.backgroundColor = "transparent"
            exit.style.border = "none"
            exit.onmouseover = function(){
                exit.style.backgroundColor = "gray"
            }
            exit.onmouseleave = function(){
                exit.style.backgroundColor = "transparent"
            }
            exit.onclick = function(){
                container.remove()
            }
            exit.style.padding = "0px"
            container.appendChild(exit)
            canvascontainer.appendChild(container)
        }
    }
    draw() {
        c.drawImage(this.image, (this.runs%3)*24, this.sy, 24, 24, this.position.x, this.position.y, 24, 24)
    }
    update() {
        this.donextmove()
        this.draw()
    }
    donextmove(){
        if(this.nextmove==0&&this.movestodo.length>0){
            this.nextmove=this.movestodo[0]
        }
        else{
            if (this.nextmove==1){
                this.sy=72
                if(this.runs==0){
                    this.runs = 4
                }else{
                    this.position.y -=3
                    this.runs -=1
                    if (this.runs==0){
                        this.nextmove = 0
                        this.movestodo = this.movestodo.splice(1,this.movestodo.length-1)
                    }
                }
            }else if (this.nextmove==2){
                this.sy=24
                if(this.runs==0){
                    this.runs = 4
                }else{
                    this.position.x -=3
                    this.runs -=1
                    if (this.runs==0){
                        this.nextmove = 0
                        this.movestodo = this.movestodo.splice(1,this.movestodo.length-1)
                    }
                }
            }
            else if (this.nextmove==3){
                this.sy=0
                if(this.runs==0){
                    this.runs = 4
                }else{
                    this.position.y +=3
                    this.runs -=1
                    if (this.runs==0){
                        this.nextmove = 0
                        this.movestodo = this.movestodo.splice(1,this.movestodo.length-1)
                    }
                }
            }
            else if (this.nextmove==4){
                this.sy=48
                if(this.runs==0){
                    this.runs = 4
                }else{
                    this.position.x +=3
                    this.runs -=1
                    if (this.runs==0){
                        this.nextmove = 0
                        this.movestodo = this.movestodo.splice(1,this.movestodo.length-1)
                    }
                }
            }
        }
    }
}

class NPC{
    constructor(id, position, looking, active){
        this.id = id
        this.width = 24
        this.height = 24
        this.inLOS = false
        this.tilestomove = 0
        this.obstruction = true
        this.moving=false
        this.runs = 0
        this.active = active
        this.position = {
            x: position.x,
            y: position.y
        }
        this.looking = looking
        this.GamePosition()
        this.image = new Image()
        this.image.src = "static/Assets/Ai.png"
        if(this.looking=="up"){
            this.sx=24
        }else if(this.looking=="down"){
            this.sx=0
        }else if(this.looking=="left"){
            this.sx=72
        }else if(this.looking=="right"){
            this.sx=48
        }
        NPCGroup.push(this)
    }
    GamePosition(){
        let x = this.position.x/12
        let y = this.position.y/12
        Game[y][x] = this
        Game[y][x+1] = this
        Game[y+1][x] = this
        Game[y+1][x+1] = this
    }
    draw() {
        c.drawImage(this.image, this.sx, (this.runs%4)*24, 24, 24, this.position.x, this.position.y, 24, 24)
    }
    update() {
        if (this.active){
            this.inlineofsight()
            if(this.inLOS==true){
                this.detectobstruction()
                if(this.obstruction==false){
                    this.moving=true
                }
            }
            if (this.moving==true){
                this.donextmove()
            }
        }
        this.draw()
    }
    inlineofsight(){
        if(this.looking == "up"){
            if(player.position.y<this.position.y&&player.position.x==this.position.x){
                this.inLOS = true
            }else{
                this.inLOS = false
            }
        }else if(this.looking=="left"){
            if(player.position.y==this.position.y&&player.position.x<this.position.x){
                this.inLOS = true
            }else{
                this.inLOS = false
            }
        }else if(this.looking == "down"){
            if(player.position.y>this.position.y&&player.position.x==this.position.x){
                this.inLOS = true
            }else{
                this.inLOS = false
            }
        }else if(this.looking=="right"){
            if(player.position.y==this.position.y&&player.position.x>this.position.x){
                this.inLOS = true
            }else{
                this.inLOS = false
            }
        }
    }
    detectobstruction(){
        if(player.runs.w==0&&player.runs.a==0&&player.runs.s==0&&player.runs.d==0){
            if(this.looking=="up"){
                let x = this.position.x/12
                let column = []
                for (let i=0;i<Game.length;i++){
                    column.push(Game[i][x])
                }
                this.tilestomove = ((this.position.y/12)-(player.position.y/12)-1)-1
                let inbetween=[]
                for(let i = (player.position.y/12)+1;i<this.position.y/12;i++){
                    inbetween.push(column[i])
                }
                if(inbetween.includes(1025)){
                    this.obstruction=true
                }else{
                    this.obstruction=false
                }
            }else if(this.looking=="left"){
                let y = this.position.y/12
                let row = Game[y]
                this.tilestomove = ((this.position.x/12)-(player.position.x/12)-1)-1
                let inbetween = []
                for(let i = (player.position.x/12)+1;i<this.position.x/12;i++){
                    inbetween.push(row[i])
                }
                if(inbetween.includes(1025)){
                    this.obstruction=true
                }else{
                    this.obstruction=false
                }
            }else if(this.looking=="down"){
                let x = this.position.x/12
                let column = []
                for (let i=0;i<Game.length;i++){
                    column.push(Game[i][x])
                }
                this.tilestomove = ((player.position.y/12)-(this.position.y/12)-1)-1
                let inbetween=[]
                for(let i = (this.position.y/12)+1;i<player.position.y/12;i++){
                    inbetween.push(column[i])
                }
                if(inbetween.includes(1025)){
                    this.obstruction=true
                }else{
                    this.obstruction=false
                }
            }else if(this.looking=="right"){
                let y = this.position.y/12
                let row = Game[y]
                this.tilestomove = ((player.position.x/12)-(this.position.x/12)-1)-1
                let inbetween = []
                for(let i = (this.position.x/12)+1;i<player.position.x/12;i++){
                    inbetween.push(row[i])
                }
                if(inbetween.includes(1025)){
                    this.obstruction=true
                }else{
                    this.obstruction=false
                }
            }
        }
    }
    donextmove(){
        if(this.tilestomove==0&&this.moving){
            this.moving = false
            socket.emit("AIbattle", this.id)
        }else{
            player.locked = true
            if(this.runs==0){
                this.tilestomove-=1
                this.runs=4
            }else{
                if(this.looking=="up"){
                    this.position.y-=3
                }else if(this.looking=="left"){
                    this.position.x-=3
                }else if(this.looking=="down"){
                    this.position.y+=3
                }else if(this.looking=="right"){
                    this.position.x+=3
                }
                this.runs-=1
            }
        }
    }
}