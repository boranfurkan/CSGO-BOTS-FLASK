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
        waxpeer.scrollTop = shadow.scrollHeight;
    })
})

function start(channel){
    mySocket.emit(channel, "start")
    this.event.target.classList.add("disabled");

}

function stop(channel){
    mySocket.emit(channel, "stop")
}

function restart(channel){
    mySocket.emit(channel, "restart")
}