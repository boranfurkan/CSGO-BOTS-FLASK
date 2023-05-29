// This function initiates a socket connection with autoConnect option set to true.
function socketConnect(){
    return io({autoConnect: true})
}

let mySocket = null // Variable to hold the socket connection.

// This function runs when the document is ready.
$(document).ready(function() {
    mySocket = socketConnect() // Initiates the socket connection.

    mySocket.on("shadowpay", function(message){
        // Listens for the "shadowpay" event from the server.
        let shadow = $("#shadow")[0]
        if(typeof message === "object"){
            // Checks if the message is an object.
            for (const log of message) {
              shadow.innerHTML += log + "\n";
              shadow.scrollTop = shadow.scrollHeight;}
              // If true, appends each log to the "shadow" element. Scrolls to the bottom of the element.
        }
        else{
            shadow.innerHTML += message + "\n";
            shadow.scrollTop = shadow.scrollHeight;
            // If false, appends the message to the "shadow" element. Scrolls to the bottom of the element.
        }
    })

    mySocket.on("waxpeer", function(message){
        // Similar to above, but for the "waxpeer" event and "waxpeer" element.
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
        // Similar to above, but for the "csgo_market" event and "csgo-market" element.
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

// This function starts a specific channel and changes its bot status to active.
function start(channel){
    mySocket.emit(channel, "start") // Emits a "start" event to the server.
    changeBotStatus(channel, true, "start")  // Changes the bot status.
}

// Similar to above, but stops a specific channel and changes its bot status to inactive.
function stop(channel){
    mySocket.emit(channel, "stop") // Emits a "stop" event to the server.
    changeBotStatus(channel, false, "stop") // Changes the bot status.
}

// This function restarts a specific channel and changes its bot status to active.
function restart(channel){
    mySocket.emit(channel, "stop") // Emits a "stop" event to the server.
    mySocket.emit(channel, "start") // Emits a "start" event to the server.
    changeBotStatus(channel, true, "restart") // Changes the bot status.
}

// This function changes the bot status and then refreshes the page.
function changeBotStatus(name, status, type) {
  // Sends a POST request to the server with the new bot status.
  fetch("/update-bot-status", {
    method: "POST",
    body: JSON.stringify({ name: name, status: status, type: type}),
  }).then(setTimeout(() => {document.location.reload();}, 10))  // Reloads the page after 10 milliseconds.
}