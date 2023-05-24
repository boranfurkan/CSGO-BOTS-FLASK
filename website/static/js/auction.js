function createCard(id, endTime, imageUrl, titleText, price, isCheaperInMarket, itemDiscount, shadowCheapest, shadowCount,
                    csMarketCheapest, csMarketCount, linkUrl, linkText) {
  let card = document.createElement('div');
  let footerInfo = document.createElement('div');
  let itemId = document.createElement('small')
  let auctionEnds = document.createElement('small')
  let img = document.createElement('img');
  let cardBody = document.createElement('div');
  let cardTitle = document.createElement('h5');
  let bodyInfo = document.createElement('div');
  let currentPrice = document.createElement('p')
  let discount = document.createElement('p')
  let shadowpayBody = document.createElement('div');
  let shadowpayCheapest = document.createElement('p');
  let shadowpayCount = document.createElement('p');
  let countGroupShadow = document.createElement('div')
  let csgoMarketBody = document.createElement('div');
  let csgoMarketCheapest = document.createElement('p');
  let csgoMarketCount = document.createElement('p')
  let countGroupMarket = document.createElement('div')
  let cardLink = document.createElement('a');
  let priceDiv = document.createElement('div')
  let empireCoin = document.createElement("img");
  let shadowpayIcon = document.createElement("img");
  let marketIcon = document.createElement("img");
  let stackIcon = document.createElement('img')


  // Set element classes as per bootstrap
  if(isCheaperInMarket) {
      card.className = 'text-white item-card gradient-border cheaper-in-market';
  }else{
      card.className = 'text-white item-card gradient-border';
  }

  card.id = `itemCard-${id}`
  bodyInfo.classList.add('info-divs');
  footerInfo.classList.add('info-divs');
  footerInfo.classList.add('card-footer')
  shadowpayBody.classList.add('info-divs');
  csgoMarketBody.classList.add('info-divs');
  auctionEnds.id = `timer-${id}`;
  auctionEnds.classList.add('text-muted');
  itemId.classList.add('text-muted');
  img.className = 'card-img-top';
  cardBody.className = 'card-body';
  cardTitle.className = 'card-title';
  cardTitle.style.height = "3rem"
  cardLink.className = 'btn btn-primary redirect-button';
  currentPrice.id = `price-${itemId}`;
  priceDiv.classList.add('price-div');
  discount.classList.add('discount');
  shadowpayIcon.classList.add("icons");
  marketIcon.className = "icons market-icon"
  countGroupShadow.classList.add('count-divs')
  countGroupMarket.classList.add('count-divs');
  stackIcon.classList.add('icons')

  // Set element content
  itemId.textContent = id;
  auctionEnds.textContent = " ";
  img.src = imageUrl;
  img.alt = 'Card image';
  cardTitle.textContent = titleText;
  currentPrice.textContent = price;
  discount.textContent = `${itemDiscount}%`;
  shadowpayCheapest.textContent = `${shadowCheapest}%`;
  shadowpayCount.textContent = shadowCount;
  csgoMarketCheapest.textContent = `${csMarketCheapest}%`;
  csgoMarketCount.textContent = csMarketCount;
  cardLink.href = linkUrl;
  cardLink.textContent = linkText;
  cardLink.target = "_blank";
  empireCoin.src = "/static/img/empire-coin.svg";
  empireCoin.alt = "empire-coin";
  shadowpayIcon.src = "/static/img/shadowpay_icon.webp";
  shadowpayIcon.alt = "shadowpay-icon";
  marketIcon.src = "/static/img/csgotm_icon.webp";
  marketIcon.alt = "csgo-market-icon";
  stackIcon.src = "/static/img/stack.svg";
  stackIcon.alt = "stack-icon";

  let clonedElem = stackIcon.cloneNode(true)
  // Append elements
  shadowpayBody.appendChild(shadowpayIcon);
  shadowpayBody.appendChild(shadowpayCheapest);
  countGroupShadow.appendChild(shadowpayCount);
  countGroupShadow.appendChild(stackIcon);
  shadowpayBody.appendChild(countGroupShadow);

  csgoMarketBody.appendChild(marketIcon);
  csgoMarketBody.appendChild(csgoMarketCheapest);
  countGroupMarket.appendChild(csgoMarketCount);
  countGroupMarket.appendChild(clonedElem);
  csgoMarketBody.appendChild(countGroupMarket);

  priceDiv.appendChild(empireCoin);
  priceDiv.appendChild(currentPrice);
  bodyInfo.appendChild(priceDiv);
  bodyInfo.appendChild(discount);
  cardBody.appendChild(cardTitle);
  cardBody.appendChild(bodyInfo);
  cardBody.appendChild(shadowpayBody)
  cardBody.appendChild(csgoMarketBody)
  cardBody.appendChild(cardLink);
  footerInfo.appendChild(itemId);
  footerInfo.appendChild(auctionEnds);
  card.appendChild(img);
  card.appendChild(cardBody);
  card.appendChild(footerInfo);
  currentPrice.parentNode.insertBefore(empireCoin, currentPrice)

  // Add the new card to the card container
  document.getElementById('card-container').appendChild(card);
}

function startTimer(id, auctionEnds) {
    const countDownDate = new Date(auctionEnds * 1000).getTime(); // Convert seconds to milliseconds

    const x = setInterval(function () {

        const now = new Date().getTime();
        const distance = countDownDate - now;

        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        document.getElementById("timer-" + id).innerHTML = minutes + "m " + seconds + "s ";

        if (distance < 0) {
            clearInterval(x);
            document.getElementById("timer-" + id).innerHTML = "EXPIRED";
            $('#itemCard-' + id).remove(); // removes the card when the auction ends
        }
    }, 1000);
}

async function checkNewItems(csgoEmpireMarketData, steamInventories, buffData, shadowpayMarketData, csgoMarketData, buffRate) {

    let newItems = await fetch("/get-new-auctions", {method: "GET"})
    newItems = await newItems.json()
    if (newItems['status'] === "success") {
        for (let item in newItems.data) {
            if (!steamInventories[item]) {
                let values = newItems.data[item];
                if (values["price"] > 40) {
                    if (buffData[item]) {
                        let itemImageUrl = "https://community.cloudflare.steamstatic.com/economy/image/" + values["url"]
                        let itemId = values["id"];
                        let auctionPrice = values["price"];
                        let auctionEnds = values["end_time"];
                        let price;
                        let isCheaperInMarket;

                        if (item in csgoEmpireMarketData) {
                            let marketPrice = csgoEmpireMarketData[item]["price"];
                            if (marketPrice < auctionPrice) {
                                price = marketPrice;
                                isCheaperInMarket = true;
                            } else {
                                price = auctionPrice;
                                isCheaperInMarket = false;
                            }
                        } else {
                            price = auctionPrice;
                            isCheaperInMarket = false;
                        }

                        // Buff Listing Check
                        let buffListing = buffData[item]["listing"];
                        let discount = (1 - (price * 0.614) / (buffListing * buffRate)) * 100;
                        discount = discount.toFixed(2);

                        if (discount >= 4) {
                            let buffBuyOrder = buffData[item]["buy_order"];
                            let buyOrderDiscount;
                            if (buffBuyOrder !== 0) {
                                buyOrderDiscount = (1 - (price * 0.614) / (buffBuyOrder * buffRate)) * 100;
                                buyOrderDiscount = buyOrderDiscount.toFixed(2);
                            } else {
                                buyOrderDiscount = "N/A";
                            }

                            let shadowpayCheapestRate;
                            let shadowpayCount;
                            if (item in shadowpayMarketData) {
                                shadowpayCheapestRate = (shadowpayMarketData[item]["price"] / buffData[item]["listing7"]).toFixed(2);
                                shadowpayCount = shadowpayMarketData[item]["count"];
                            } else {
                                shadowpayCheapestRate = 0;
                                shadowpayCount = 0;
                            }

                            let csgoMarketCheapestRate;
                            let csgoMarketCount;
                            if (item in csgoMarketData) {
                                csgoMarketCheapestRate = (csgoMarketData[item]["price"] / buffData[item]["listing7"]).toFixed(2);
                                csgoMarketCount = csgoMarketData[item]["count"];
                            } else {
                                csgoMarketCheapestRate = 0;
                                csgoMarketCount = 0;
                            }

                            const linkUrl = `https://csgoempire.com/item/${itemId}`
                            if (!$(`#itemCard-${itemId}`)[0]){
                                createCard(itemId, auctionEnds, itemImageUrl, item, auctionPrice, isCheaperInMarket, discount, shadowpayCheapestRate, shadowpayCount,
                                    csgoMarketCheapestRate, csgoMarketCount, linkUrl, "More Info")
                                startTimer(itemId, auctionEnds)}

                            else{
                                $(`#price-${itemId}`).text(price)
                            }
                        }
                    }
                }
            }
        }
    } else {
        showToast("Error", newItems.details, "warning")
    }
}
