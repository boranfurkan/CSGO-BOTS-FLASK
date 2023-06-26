// The ready event occurs when the DOM (document object model) has been loaded.
// Once it's loaded, it checks the active page and adds a search logo.
$(document).ready(function() {
  checkActivePage()
  addSearchLogo()
})

// This function creates and displays a toast notification with the given header, content and style.
function showToast(header, content, style) {
  var toastEl = document.createElement('div');  // Create a new div element for the toast.
  toastEl.classList.add('toast'); // Add the "toast" class to the div.
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');
  toastEl.style.backgroundColor = "#fab007!important"
  // Set the toast style
  if (style) {
    toastEl.classList.add('bg-' + style);
  }

  // Create the toast header element
  var toastHeaderEl = document.createElement('div'); // Create a new div element for the toast header.
  toastHeaderEl.classList.add('toast-header');  // Add the "toast-header" class to the div.
  toastHeaderEl.style.backgroundColor = '#fff'
  toastHeaderEl.style.borderBottom = "none"
  toastHeaderEl.innerHTML = '<strong class="me-auto">' + header + '</strong>' +
    '<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>';

  // Create the toast body element
  var toastBodyEl = document.createElement('div'); // Create a new div element for the toast body.
  toastBodyEl.classList.add('toast-body'); // Add the "toast-body" class to the div.
  toastBodyEl.textContent = content;
  if(style==="success"){
      toastBodyEl.style.backgroundColor = '#fab007'
  }

  // Add the header and body elements to the toast element
  toastEl.appendChild(toastHeaderEl);
  toastEl.appendChild(toastBodyEl);

  // Add the toast element to the container
  var toastContainerEl = document.querySelector('.toast-container');
  toastContainerEl.appendChild(toastEl);

  // Show the toast
  var toast = new bootstrap.Toast(toastEl); // Create a new bootstrap toast with the div.
  toast.show(); // Show the toast.
}

function checkActivePage(){
  switch(window.location.pathname) {
  // If the active page is Home, highlight the Home link.
  //... (repeat for each case)
  case "/":
    $("#home")[0].classList.add("active")
    break;
  case "/auction":
  $("#auction")[0].classList.add("active")
    break;
  case "/items":
    $("#items")[0].classList.add("active")
    break;
  case "/configs":
    $("#configs")[0].classList.add("active")
    $('#configs-form').ajaxForm({
        url : '/configs',
        dataType : 'json',
        success : function (response) {
            if(response.status === "success"){
              showToast('Success', response.details, 'success');
            }else{
              showToast('Error', response.details, 'danger');
            }
        }
    })
    break;
  case "/login":
    $("#login")[0].classList.add("active")
    break;
  case "/sign-up":
    $("#signUp")[0].classList.add("active")
    break;}
}

// This function updates an item's price based on user input.
function updateItem(itemId, type) {
  const newSuggestedPrice = document.getElementById(itemId).value;

  // Specifies the HTTP method to be used (PATCH).
  fetch("/update-item", {
    method: "PATCH",
    body: JSON.stringify({ itemId: itemId, type:type, newSuggestedPrice: newSuggestedPrice}),
  }).then((_res) => {
    // Checks if the fetch request was successful.
    // If successful, display a success toast, otherwise, display an error toast and reload the page.
    if(_res.ok){
      document.getElementById(itemId).value = newSuggestedPrice
      showToast('Success', 'The operation was successful!', 'success');
    }else{
      showToast('Error', _res.statusText, 'danger');
      location.reload()
    }
  });
}

// This function adds a search icon to the search field on the items page.
function addSearchLogo(){
  if(window.location.pathname === "/items"){
    const newNode = document.createElement("i");
    newNode.classList.add("fa-brands")
    newNode.classList.add("fa-searchengin")
    const element = $(".search-input")[0]
    element.setAttribute("placeholder", "Enter Your Search Here")
    $(newNode).insertAfter(element)
  }
}