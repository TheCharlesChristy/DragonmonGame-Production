const userButtonContainer = document.getElementById('user-buttons');
const messageContainer = document.getElementById("messages")
const body = document.getElementById("body")
const textinput = document.getElementById("text-input")
const submit = document.getElementById("submit-button")
const ManageButton = document.getElementById("Manage-button")
const listofmembers = []
const socket = io('https://localhost:1111')
var currentconvo = ""
var currentconvotype = ""
const friends = []
const Groupnames = []
const Groupids = []
socket.on('connect',function(){ 
  socket.emit("Finalise", username)
  socket.emit("Requestconversations")
  socket.on("Recieveconversations", (frienddict, Groupnamedict, Groupiddict) => {
    let friendslist = Object.values(frienddict)
    let Groupnameslist = Object.values(Groupnamedict)
    let Groupidslist = Object.values(Groupiddict)
    for (i=0;i<friendslist.length;i++){
        friends.push(friendslist[i])
    }
    for (i=0;i<Groupnameslist.length;i++){
        Groupnames.push(Groupnameslist[i])
        Groupids.push(Groupidslist[i])
    }
    updateconversationtable(friends)
  })
})

function ReverseList(list){
    let reversedlist = []
    for (let i = 0; i < list.length; i++) {
        let previousitem = list.length - (i+1)
        let lastitem = list[previousitem]
        reversedlist.push(lastitem)
    }
    return reversedlist
}

function updateconversationtable(friendnames){
    const elements = document.getElementsByClassName("username-button")
    while(elements.length > 0){
        elements[0].parentNode.removeChild(elements[0])
    }
    // Loop through the usernames and create a button for each one
    for (let i = 0; i < friendnames.length; i++) {
        const friendname = friendnames[i];
        const button = document.createElement('button');
        button.id = "friendbutton"
        button.innerHTML = friendname;
        button.classList.add('username-button');
        button.addEventListener('click', function() {
            currentconvotype = "Friend"
            ClearPage()
            textinput.style.display = "block"
            submit.style.display = "block"
            const allbuttons = document.getElementsByClassName("username-button")
            for (i = 0; i<allbuttons.length; i++){
                allbuttons[i].style.backgroundColor = "white"
            }
            button.style.backgroundColor = "rgb(25, 224, 246)"
            currentconvo = friendname
            ShowMessages()
        })
        userButtonContainer.appendChild(button);
    }
    for (let i = 0; i < Groupnames.length; i++) {
        const Groupname = Groupnames[i];
        const Groupid = Groupids[i]
        const button = document.createElement('button');
        button.id = "friendbutton"
        button.innerHTML = Groupname;
        button.classList.add('username-button');
        button.addEventListener('click', function() {
            ClearPage()
            currentconvotype = "Group"
            textinput.style.display = "block"
            submit.style.display = "block"
            const allbuttons = document.getElementsByClassName("username-button")
            for (i = 0; i<allbuttons.length; i++){
                allbuttons[i].style.backgroundColor = "white"
            }
            button.style.backgroundColor = "rgb(25, 224, 246)"
            currentconvo = Groupid
            ShowMessages()
        })
        userButtonContainer.appendChild(button);
    }
}

function updatemessages(Messages){
    const elements = document.querySelectorAll(".message")
    //shrink all the elements
    elements.forEach((element) => {
        element.classList.remove("item")
        element.classList.remove("start")
        element.classList.add("shrink")
    })
    let timegap
    if (elements.length>0){
        timegap = 500
    }else{
        timegap = 0
    }
    //wait for the shrink to finish
    setTimeout(function(){
        //remove all the elements
        elements.forEach((element) => {
            element.remove()
        })
        //create all the new elements
        Messages.forEach((message) => {
            const newmessage = document.createElement("p")
            newmessage.classList.add("message")
            newmessage.classList.add("start")
            newmessage.innerHTML = message
            messageContainer.appendChild(newmessage)
        })
        //wait for the elements to be created
        setTimeout(function(){
            //make all the elements appear
            const elements = document.querySelectorAll(".message")
            elements.forEach((element) => {
                element.classList.remove("start")
                element.classList.remove("shrink")
                element.classList.add("item")
                messageContainer.scrollTop = messageContainer.scrollHeight;
            })
        },100)
    }, timegap)
}

socket.on("Recievemessages", (Messagesdict) =>{
    messages = Object.values(Messagesdict)
    if (ManageButton.innerHTML == "Manage Conversation"){
        updatemessages(messages)
    }
})

document.addEventListener("keydown", (event)=>{
    if(event.key==="Enter"){
        Sendmessage()
    }
  })

function Sendmessage(){
    messagetogo = textinput.value
    if (textinput.value.length < 150){
        socket.emit("SendMessage", messagetogo, currentconvo)
        setTimeout(function(){
            textinput.value = ""
        }, 100)
    }
    else{
        alert("Message too long (150 character limit)")
        setTimeout(function(){
            textinput.value = messagetogo
        }, 100)
    }
}

function Goback(){
    b.classList.remove("item")
    b.classList.add("shrink")
    setTimeout(function(){
        socket.emit("GoBack")
    }, 500)
}

socket.on("ToGame", (message) =>{
    playerid = message.PID
    location.href = "https://localhost:1111/Game?data="+ playerid
})

function ManageConversation() {
    ManageButton.innerHTML = "Show Messages"
    ManageButton.onclick = ShowMessages
    ClearPage()
    t.classList.remove("item")
    t.classList.add("shrink")
    s.classList.remove("item")
    s.classList.add("shrink")
    setTimeout(function(){
        const ClearConversationbutton = document.createElement('button')
        ClearConversationbutton.id = "ClearConversation"
        ClearConversationbutton.classList.add("ClearConversation")
        ClearConversationbutton.classList.add("start")
        ClearConversationbutton.innerHTML = "Clear Conversation"
        ClearConversationbutton.onclick = ClearConversation
        body.appendChild(ClearConversationbutton)
        const CreateGroupbutton = document.createElement('button')
        CreateGroupbutton.id = "CreateGroup"
        CreateGroupbutton.classList.add("CreateGroup")
        CreateGroupbutton.classList.add("start")
        CreateGroupbutton.innerHTML = "Create message group"
        CreateGroupbutton.addEventListener("click", function(){
            CreateGroup("Create", friends)
        })
        body.appendChild(CreateGroupbutton)
        setTimeout(function(){
            ClearConversationbutton.classList.remove("start")
            CreateGroupbutton.classList.remove("start")
            ClearConversationbutton.classList.add("item")
            CreateGroupbutton.classList.add("item")
            if (currentconvotype == "Group"){
                const leavebutton = document.createElement("button")
                const AddmemberButton = document.createElement("button")
                leavebutton.id = "leavebutton"
                leavebutton.classList.add("leavebutton")
                leavebutton.classList.add("start")
                leavebutton.innerHTML = "Leave Group"
                leavebutton.addEventListener("click", function() {
                    socket.emit("LeaveGroup", currentconvo)
                })
                AddmemberButton.id = "addmember"
                AddmemberButton.classList.add("addmember")
                AddmemberButton.classList.add("start")
                AddmemberButton.innerHTML = "Add member"
                AddmemberButton.addEventListener("click", function() {
                    socket.emit("GetMembers", currentconvo)
                    socket.on("GroupMembers", (Members) => {
                        let Memberslist = Object.values(Members)
                        let nonmemberlist = []
                        for (let i = 0; i<friends.length;i++){
                            if (Memberslist.includes(friends[i])==false){
                                nonmemberlist.push(friends[i])
                            }
                        }
                        CreateGroup("Add", nonmemberlist)
                    })
                })
                body.appendChild(AddmemberButton)
                body.appendChild(leavebutton)
                setTimeout(function(){
                    leavebutton.classList.remove("start")
                    AddmemberButton.classList.remove("start")
                    leavebutton.classList.add("item")
                    AddmemberButton.classList.add("item")
                }, 100)
            }
        }, 100)
    },500)
}

function ShowMessages() {
    ClearPage()
    showmsgcontrols()
    ManageButton.innerHTML = "Manage Conversation"
    ManageButton.onclick = ManageConversation
    textinput.style.display = "block"
    submit.style.display = "block"
    if (currentconvo != ""){
        if (currentconvotype == "Friend"){
            socket.emit("Requestfriendmessages", currentconvo)
        }else{
            socket.emit("RequestGroupconversation", currentconvo)
        }
    }
}

function showmsgcontrols(){
    t.classList.remove("item")
    s.classList.remove("item")
    m.classList.remove("item")
    t.classList.remove("start")
    t.classList.remove("shrink")
    t.classList.add("item")
    s.classList.remove("start")
    s.classList.remove("shrink")
    s.classList.add("item")
    m.classList.remove("start")
    m.classList.remove("shrink")
    m.classList.add("item")
}
function Hidemsgcontrols(){
    t.classList.remove("item")
    t.classList.add("shrink")
    s.classList.remove("item")
    s.classList.add("shrink")
    m.classList.remove("item")
    m.classList.add("shrink")
}


function ClearConversation() {
    if (currentconvo != ""){
        socket.emit("ClearMessages", currentconvo)
    }
}



function ClearPage() {
    let setelements = []
    let ClearConversationbutton = document.getElementById("ClearConversation")
    let CreateGroupbutton = document.getElementById("CreateGroup")
    let membertable = document.getElementById("membertable")
    let addmember = document.getElementById("addmember")
    let leavegroup = document.getElementById("leavebutton")
    let messages = document.querySelectorAll(".message")
    if (messages != null){
        messages.forEach((message) => {
            message.classList.remove("item")
            message.classList.remove("start")
            message.classList.add("shrink")
            setelements.push(message)
        })
    }
    if (CreateGroupbutton != null){
        setelements.push(CreateGroupbutton)
        CreateGroupbutton.classList.remove("item")
        CreateGroupbutton.classList.remove("start")
        CreateGroupbutton.classList.add("shrink")
    }
    if (ClearConversationbutton != null){
        setelements.push(ClearConversationbutton)
        ClearConversationbutton.classList.remove("item")
        ClearConversationbutton.classList.remove("start")
        ClearConversationbutton.classList.add("shrink")
    }
    if (membertable != null){
        setelements.push(membertable)
        membertable.classList.remove("item")
        membertable.classList.remove("start")
        membertable.classList.add("shrink")
    }
    if (addmember != null){
        setelements.push(addmember)
        addmember.classList.remove("item")
        addmember.classList.remove("start")
        addmember.classList.add("shrink")
    }
    if (leavegroup != null){
        setelements.push(leavegroup)
        leavegroup.classList.remove("item")
        leavegroup.classList.remove("start")
        leavegroup.classList.add("shrink")
    }
    setTimeout(function(){
        setelements.forEach((element) => {
            element.remove()
        })
    }, 500)
}

function CreateGroup(reference, array) {//here
    ManageButton.innerHTML = "Back"
    ManageButton.onclick = Back
    ClearPage()
    const membertable = document.createElement("table")
    membertable.classList.add("membertable")
    membertable.id = "membertable"
    array.forEach(friend => {
        let row = document.createElement("tr")
        let cell = document.createElement("td")
        cell.innerText = friend
        row.appendChild(cell)
        let buttonCell = document.createElement("td") // create a new cell for the button
        let button = document.createElement("button") // create the button element
        button.innerText = "Add" // set the button text
        button.classList.add("Addmember") // add a class to the button for styling
        button.dataset.friend = friend // store the friend name as a data attribute on the button
        if (reference == "Create"){
            button.addEventListener("click", ChangeMember) // add a click event listener to the button
        }
        else if (reference == "Add"){
            button.addEventListener("click", AddMember)
        }
        buttonCell.appendChild(button) // add the button to the new cell
        row.appendChild(buttonCell) // add the new cell to the row
        membertable.appendChild(row)
    })
    if(reference=="Create"){
        let row = document.createElement("tr")
        let buttonCell = document.createElement("td") // create a new cell for the button
        let button = document.createElement("button") // create the button element
        button.innerText = "Create Group" // set the button text
        button.id = "CreateGroup"
        button.classList.add("Addmember") // add a class to the button for styling
        button.addEventListener("click", FinishGroup) // add a click event listener to the button
        buttonCell.appendChild(button) // add the button to the new cell
        row.appendChild(buttonCell) // add the new cell to the row
        membertable.appendChild(row)

        let row2 = document.createElement("tr")
        let Cell = document.createElement("td")
        let Groupname = document.createElement("input")
        Groupname.id = "Groupname" 
        Groupname.type = "text"
        Groupname.placeholder = "Groupname"
        Groupname.minLength = 10
        Cell.appendChild(Groupname) 
        row2.appendChild(Cell) 
        membertable.appendChild(row2)
    }
    membertable.classList.add("start")
    body.appendChild(membertable)
    setTimeout(() => {
        membertable.classList.remove("start")
        membertable.classList.add("item")
    }, 100);
}


function Back() {
    ManageConversation()
}

function ChangeMember(event){
    let button = event.target
    let membername = event.target.dataset.friend
    if (button.innerText == "Add"){
        listofmembers.push(membername)
        button.innerText = "Added"
    }
    else{
        let index = listofmembers.indexOf(membername)
        listofmembers.splice(index, 1)
        button.innerText = "Add"
    }
}

function AddMember(event){
    targetname = event.target.dataset.friend
    socket.emit("AddMember", targetname, currentconvo)
}

function FinishGroup(){
    let Groupnamebox = document.getElementById("Groupname")
    let Groupname = Groupnamebox.value
    if (Groupname != null){
        socket.emit("CreateGroup", listofmembers, Groupname)
        while(listofmembers.length > 0) {
            listofmembers.pop();
        }
        CreateGroup("Create", friends)
    }
    else{
        alert("Please Input a Group name")
    }
}

socket.on("Notenoughmembers", function(){
    CreateGroup("Create", friends)
    errormessage = document.createElement("p")
    errormessage.innerHTML = "Not Enough Members"
    errormessage.classList = "Error"
    body.appendChild(errormessage)
})

socket.on("refresh", function(){
    socket.emit("Redirecting")
    socket.on("Redirectconfirmed", (message) => {
        let Token = message.token
        b.classList.remove("item")
        b.classList.remove("start")
        b.classList.add("shrink")
        setTimeout(function(){
            location.href = "https://localhost:1111/Messages?token="+Token
        }, 500)
    })
})