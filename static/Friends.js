const FriendsTable = document.querySelector("#data-table-body")
const RequestsTable = document.querySelector("#request-table-body")
const socket = io('https://localhost:1111')
socket.on('connect',function(){ 
  socket.emit("getFriends", Token)
  socket.emit("getRequests")
})
socket.on("RecieveFriends", (friends) => {
  data = Object.values(friends)
  updatefriendstable(data)
})
socket.on("UpdateTable", function(){
  b.classList.remove("item")
  b.classList.add("shrink")
  setTimeout(() => {
    location.reload()
  }, 500)
})
function updatefriendstable(data){
  let numrows = FriendsTable.rows.length
  console.log(numrows)
  for(let i=0;i<numrows;i++){
    FriendsTable.deleteRow(i)
  }
  data.forEach(item => {
    let row = document.createElement("tr")
    let cell = document.createElement("td")
    cell.innerText = item
    row.appendChild(cell)

    let buttonCell = document.createElement("td") // create a new cell for the button
    let button = document.createElement("button") // create the button element
    button.innerText = "Remove" // set the button text
    button.classList.add("remove-button") // add a class to the button for styling
    button.dataset.friend = item // store the friend name as a data attribute on the button
    button.addEventListener("click", removeFriend) // add a click event listener to the button
    buttonCell.appendChild(button) // add the button to the new cell
    row.appendChild(buttonCell) // add the new cell to the row

    FriendsTable.appendChild(row)
  })
}

function updaterequeststable(data){
  data.forEach(item => {
    let row = document.createElement("tr")
    let cell = document.createElement("td")
    cell.innerText = item
    row.appendChild(cell)

    let buttonCell = document.createElement("td") // create a new cell for the button
    let button = document.createElement("button") // create the button element
    button.innerText = "Accept" // set the button text
    button.classList.add("accept-button") // add a class to the button for styling
    button.dataset.friend = item // store the friend name as a data attribute on the button
    button.addEventListener("click", Acceptfriend) // add a click event listener to the button
    buttonCell.appendChild(button) // add the button to the new cell
    let button2 = document.createElement("button") // create the button element
    button2.innerText = "Decline" // set the button text
    button2.classList.add("remove-button") // add a class to the button for styling
    button2.dataset.friend = item // store the friend name as a data attribute on the button
    button2.addEventListener("click", Declinefriend) // add a click event listener to the button
    buttonCell.appendChild(button2) // add the button to the new cell
    row.appendChild(buttonCell) // add the new cell to the row
    console.log(row)
    RequestsTable.appendChild(row)
  })
}


function removeFriend(event) {
  let friendName = event.target.dataset.friend
  socket.emit("removeFriend", Token, friendName)
}

document.addEventListener("keydown", (event)=>{
  if(event.key==="Enter"){
    searchname()
  }
})

function searchname() { 
  let querydata = document.getElementById("friend-name").value
  socket.emit("searchName", querydata)
}

socket.on("Nameresult", (namejson) => {
  let Name = namejson.data
  if (Name != "None"){
    label = document.getElementById("Targetname")
    label.innerHTML = Name
    button = document.getElementById("Addfriend")
    button.style.display = "block"
  }else{
    alert("This Account does not exist")
  }
})

socket.on("Friendrequests", (requests) => {
  data = Object.values(requests)
  updaterequeststable(data)
})
function Sendfriendrequest() {
  friendname = document.getElementById("Targetname").innerHTML
  let button = document.getElementById("Addfriend")
  button.innerHTML = "Sent"
  socket.emit("SendFriendRequest", friendname)
}

function Acceptfriend(event){
  let friendName = event.target.dataset.friend
  socket.emit("AcceptFriend", Token, friendName)
  b.classList.remove("item")
  b.classList.add("shrink")
  setTimeout(() => {
    location.reload()
  }, 500)
}

function Declinefriend(event){
  let Targetname = event.target.dataset.friend
  socket.emit("DeclineFriend", Token, Targetname)
  b.classList.remove("item")
  b.classList.add("shrink")
  setTimeout(() => {
    location.reload()
  }, 500)
}

function Goback(){
  b.classList.remove("item")
  b.classList.add("shrink")
  setTimeout(() => {
    socket.emit("GoBack")
  }, 500);
}

socket.on("ToGame", (message) =>{
  playerid = message.PID
  location.href = "https://localhost:1111/Game?data="+ playerid
})