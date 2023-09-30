keysdown = {
  w: false,
  a: false,
  s: false,
  d: false
}

function MainLoop() {
  if (start==true){
    background.draw()
    player.update()
    for (let i =0;i<NPCGroup.length;i++){
      let AI = NPCGroup[i]
      AI.update()
    }
    for (let i =0;i<FriendGroup.length;i++){
      let friend = FriendGroup[i]
      friend.update()
    }
    background.drawtop()
  }
  window.requestAnimationFrame(MainLoop)
}
MainLoop()

document.addEventListener("keydown", function(event){
  key = event.key.toLowerCase()
  if (key=="w"){
    keysdown.w = true
  }
  if (key=="a"){
    keysdown.a = true
  }
  if (key=="s"){
    keysdown.s = true
  }
  if (key=="d"){
    keysdown.d = true
  }
  if (key=="r"){
    player.position.x = 180
    player.position.y = 180
    socket.emit("Resetplayer")
  }
})
document.addEventListener("keyup", function(event){
  key = event.key.toLowerCase()
  if (key=="w"){
    keysdown.w = false
  }
  if (key=="a"){
    keysdown.a = false
  }
  if (key=="s"){
    keysdown.s = false
  }
  if (key=="d"){
    keysdown.d = false
  }
})
canvas.addEventListener("click", function(event){
  let rect = canvas.getBoundingClientRect();
  let ox = event.clientX - rect.left;
  let oy = event.clientY - rect.top;
  let coords = adjustcoords(ox, oy, rect)
  let x = coords.x
  let y = coords.y
  //problem with this code is, if the screen is not 900:600 then the friend's position isnt updated accordingly
  //need to do some maths??
  for(let i = 0; i<FriendGroup.length; i++){
    let currentfriend = FriendGroup[i]
    if(x>=currentfriend.position.x && x<=currentfriend.position.x+24 && y>=currentfriend.position.y && y<=currentfriend.position.y+24){
      currentfriend.doclick()
    }
  }
})

adjustcoords = function(x, y, rect){
  //find the game tile clicked on
  width = rect.right-rect.left
  height = rect.bottom-rect.top
  tilewidth = width/75
  tileheight = height/50
  xtile = Math.floor(x/tilewidth)
  ytile = Math.floor(y/tileheight)
  //finish converting to si
  x = xtile*12
  y = ytile*12
  return {"x": x, "y": y}
}
