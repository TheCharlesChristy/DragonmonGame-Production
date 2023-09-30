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
socket.on("Items", (data) => {
    let Itemids = Object.values(data)
    for (let i=0;i<Itemids.length;i++){
        var newitem = new Item(Itemids[i])
        Items.push(newitem)
    }
})
socket.on("Quantities", (data) => {
    Quantities = Object.values(data)
    for (let i=0;i<Quantities.length;i++){
        const item = Items[i]
        item.GetAmount(Quantities[i])
    }
    canvasToTable()
})


function canvasToTable() {
    oldtable = document.getElementById("Itemtable")
    const table = document.createElement('table');
    const tbody = document.createElement('tbody');
    table.style.width = "100%"
    tbody.classList.add("itemtablebody")
    table.id = "Itemtable"
    for (let y = 0; y < Items.length+1; y++) {
      const row = document.createElement('tr');
      row.classList.add("itemrow")
      for (let x = 0; x < 4; x++) {
        const cell = document.createElement('td');
        cell.classList.add("itemcell")
        if (x==0){
            if(y==0){
                let head = document.createElement("p")
                head.classList.add("tabletext")
                head.innerHTML = "Item"
                cell.appendChild(head)
            }else{
                const currentitem = Items[y-1]
                let text = document.createElement("p")
                text.classList.add("tabletext")
                try{
                    text.innerHTML = currentitem.itemname
                    cell.appendChild(text)
                }catch{
                    console.log("Invalid item")
                }
            }
        }else if (x==1){
            if(y==0){
                let head = document.createElement("p")
                head.classList.add("tabletext")
                head.innerHTML = "Description"
                cell.appendChild(head)
            }else{
                const currentitem = Items[y-1]
                let text = document.createElement("p")
                text.classList.add("tabletext")
                try{
                    text.innerHTML = currentitem.itemdescription
                    cell.appendChild(text)
                }catch{
                    console.log("Invalid item")
                }
            }
        }else if (x==2){
            if(y==0){
                let head = document.createElement("p")
                head.classList.add("tabletext")
                head.innerHTML = "Quantity"
                cell.appendChild(head)
            }else{
                const currentitem = Items[y-1]
                let text = document.createElement("p")
                text.classList.add("tabletext")
                try{
                    text.innerHTML = currentitem.Amount
                    cell.appendChild(text)
                }catch{
                    console.log("Invalid item")
                }
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
        //Case of team=open
    }
  }