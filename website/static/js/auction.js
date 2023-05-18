const domain = "csgoempire.com";
const socketEndpoint = `wss://trade.${domain}/trade`;

$(document).ready(function() {
  initSocket();
})


function initSocket(userData) {
    try {
        const socket = io(socketEndpoint, {
            path: "/s/",
            transports: ["websocket"],
            extraHeaders: { "User-agent": `${userData.user.id} API Bot` },
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

function createCard(imageUrl, titleText, descriptionText, linkUrl, linkText) {
  let card = document.createElement('div');
  let img = document.createElement('img');
  let cardBody = document.createElement('div');
  let cardTitle = document.createElement('h5');
  let cardText = document.createElement('p');
  let cardLink = document.createElement('a');

  // Set element classes as per bootstrap
  card.className = 'card';
  card.style.width = '18rem';
  img.className = 'card-img-top';
  cardBody.className = 'card-body';
  cardTitle.className = 'card-title';
  cardText.className = 'card-text';
  cardLink.className = 'btn btn-primary';

  // Set element content
  img.src = imageUrl;
  img.alt = 'Card image';
  cardTitle.textContent = titleText;
  cardText.textContent = descriptionText;
  cardLink.href = linkUrl;
  cardLink.textContent = linkText;

  // Append elements
  cardBody.appendChild(cardTitle);
  cardBody.appendChild(cardText);
  cardBody.appendChild(cardLink);
  card.appendChild(img);
  card.appendChild(cardBody);

  // Add the new card to the card container
  document.getElementById('cardContainer').appendChild(card);
}