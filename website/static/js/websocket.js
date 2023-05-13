function socketConnect(){
    return io({autoConnect: true})
}

let mySocket = null

$(document).ready(function() {
    mySocket = socketConnect()

    mySocket.on("shadowpay", function(message){
        let shadow = $("#shadow")[0]
        if(typeof message === "object"){
            for (const log of message) {
              shadow.innerHTML += log + "\n";
              shadow.scrollTop = shadow.scrollHeight;}
        }
        else{
            shadow.innerHTML += message + "\n";
            shadow.scrollTop = shadow.scrollHeight;
        }
    })

    mySocket.on("waxpeer", function(message){
        let waxpeer = $("#waxpeer")[0]
        if(typeof message === "object"){
            for (const log of message) {
              waxpeer.innerHTML += log + "\n";
              waxpeer.scrollTop = waxpeer.scrollHeight;}
        }
        else{
            waxpeer.innerHTML += message + "\n";
            waxpeer.scrollTop = waxpeer.scrollHeight;
        }
    })

    mySocket.on("csgo_market", function(message){
        let csgoMarket = $("#csgo-market")[0]
        if(typeof message === "object"){
            for (const log of message) {
              csgoMarket.innerHTML += log + "\n";
              csgoMarket.scrollTop = csgoMarket.scrollHeight;}
        }
        else{
            csgoMarket.innerHTML += message + "\n";
            csgoMarket.scrollTop = csgoMarket.scrollHeight;
        }
    })
})

function start(channel){
    mySocket.emit(channel, "start")
    changeBotStatus(channel, true, "start")
}

function stop(channel){
    mySocket.emit(channel, "stop")
    changeBotStatus(channel, false, "stop")
}

function restart(channel){
    mySocket.emit(channel, "stop")
    mySocket.emit(channel, "start")
    changeBotStatus(channel, true, "restart")
}

function changeBotStatus(name, status, type) {
  fetch("/update-bot-status", {
    method: "POST",
    body: JSON.stringify({ name: name, status: status, type: type}),
  }).then(setTimeout(() => {document.location.reload();}, 10))
}