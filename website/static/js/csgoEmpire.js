const domain = "csgoempire.com";
const socketEndpoint = `wss://trade.${domain}/trade`;

async function initSocket(userData) {
    try {
        const socket = io(socketEndpoint, {
            path: "/s/",
            transports: ["websocket"],
            extraHeaders: { "User-agent": `5265639 API Bot` },
            secure: true,
            rejectUnauthorized: false,
            reconnect: true,
        });

        socket.on("connect", async () => {
            socket.on("init", (data) => {
                if (data && data.authenticated) {
                    console.log(`Successfully authenticated as ${data.name}`);

                    // Emit the default filters to ensure we receive events
                    socket.emit("filters", {
                        price_max: 9999999,
                    });
                } else {
                    socket.emit("identify", {
                        uid: userData.user.id,
                        model: userData.user,
                        authorizationToken: userData.socket_token,
                        signature: userData.socket_signature,
                    });
                }
            });

            socket.on("timesync", (data) =>
                console.log(`Timesync: ${JSON.stringify(data)}`)
            );

            socket.on("new_item", (data) =>
                console.log(`new_item: ${JSON.stringify(data)}`)
            );

            socket.on("auction_update", (data) =>
                console.log(`auction_update: ${JSON.stringify(data)}`)
            );

            socket.on("disconnect", (reason) =>
                console.log(`Socket disconnected: ${reason}`)
            );
        });

        // Listen for the following event to be emitted by the socket in error cases
        socket.on("close", (reason) =>
            console.log(`Socket closed: ${reason}`)
        );

        socket.on("error", (data) => console.log(`WS Error: ${data}`));
        socket.on("connect_error", (data) =>
            console.log(`Connect Error: ${data}`)
        );
    }
    catch (e) {
        console.log(`Error while initializing the Socket. Error: ${e}`);
    }
}

$(document).ready(function() {
  initSocket();
})
