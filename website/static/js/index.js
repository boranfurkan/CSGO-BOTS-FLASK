function updateItem(itemId) {
  const newSuggestedPrice = document.getElementById(itemId).value;
  fetch("/update-item", {
    method: "PATCH",
    body: JSON.stringify({ itemId: itemId, newSuggestedPrice: newSuggestedPrice}),
  }).then((_res) => {
    if(_res.ok){
      document.getElementById(itemId).value = newSuggestedPrice
    }else{
      console.log(_res.statusText)
      window.location.href = "/configs";
    }
  });
}
