function socketConnect(){
    return io({autoConnect: true})
}

let mySocket = null

$(document).ready(function() {
    mySocket = socketConnect()

    mySocket.on("shadowpay", function(message){
        let shadow = $("#shadow")[0]
        shadow.innerHTML += message + "\n";
        shadow.scrollTop = shadow.scrollHeight;
    })

    mySocket.on("waxpeer", function(message){
        let waxpeer = $("#waxpeer")[0]
        waxpeer.innerHTML += message + "\n";
        waxpeer.scrollTop = waxpeer.scrollHeight;
    })

    mySocket.on("csgo_market", function(message){
        let csgoMarket = $("#csgo-market")[0]
        csgoMarket.innerHTML += message + "\n";
        csgoMarket.scrollTop = csgoMarket.scrollHeight;
    })
})

function start(channel){
    mySocket.emit(channel, "start")
    changeBotStatus(channel, true)
    setTimeout(() => {document.location.reload();}, 100);
}

function stop(channel){
    mySocket.emit(channel, "stop")
    changeBotStatus(channel, false)
    setTimeout(() => {document.location.reload();}, 100);
}

function restart(channel){
    mySocket.emit(channel, "stop")
    setTimeout(() => {document.location.reload();}, 100);
    mySocket.emit(channel, "start")
    changeBotStatus(channel, true)
}

function changeBotStatus(name, status) {
  fetch("/update-bot-status", {
    method: "POST",
    body: JSON.stringify({ name: name, status: status}),
  }).then((_res) => {
    if(_res.ok){
      console.log("success")
    }else{
      console.log(_res.statusText)
      window.location.href = "/configs";
    }
  });
}