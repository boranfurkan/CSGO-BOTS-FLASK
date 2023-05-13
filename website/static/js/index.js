$(document).ready(function() {
  checkActivePage()
  addSearchLogo()
})

function showToast(header, content, style) {
  var toastEl = document.createElement('div');
  toastEl.classList.add('toast');
  toastEl.setAttribute('role', 'alert');
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.setAttribute('aria-atomic', 'true');
  toastEl.style.backgroundColor = "#fab007!important"
  // Set the toast style
  if (style) {
    toastEl.classList.add('bg-' + style);
  }

  // Create the toast header element
  var toastHeaderEl = document.createElement('div');
  toastHeaderEl.classList.add('toast-header');
  toastHeaderEl.style.backgroundColor = '#fff'
  toastHeaderEl.style.borderBottom = "none"
  toastHeaderEl.innerHTML = '<strong class="me-auto">' + header + '</strong>' +
    '<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>';

  // Create the toast body element
  var toastBodyEl = document.createElement('div');
  toastBodyEl.classList.add('toast-body');
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
  var toast = new bootstrap.Toast(toastEl);
  toast.show();
}

function checkActivePage(){
  switch(window.location.pathname) {
  case "/":
    $("#home")[0].classList.add("active")
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

function updateItem(itemId) {
  const newSuggestedPrice = document.getElementById(itemId).value;
  fetch("/update-item", {
    method: "PATCH",
    body: JSON.stringify({ itemId: itemId, newSuggestedPrice: newSuggestedPrice}),
  }).then((_res) => {
    if(_res.ok){
      document.getElementById(itemId).value = newSuggestedPrice
      showToast('Success', 'The operation was successful!', 'success');
    }else{
      showToast('Error', _res.statusText, 'danger');
      location.reload()
    }
  });
}

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