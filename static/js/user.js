let shareBtn = document.getElementById("share-btn");
let deleteBtn = document.getElementById("delete-btn");
let profileBtn = document.getElementById("profile-btn");
let profile = document.querySelector(".profile");
let closeBtn = document.querySelector(".close-btn");
let modalWindow = document.getElementById("modal-window");
let modalCloseBtn = document.getElementsByClassName("close")[0];

// Share Button
shareBtn.addEventListener("click", function () {
  if (!modalWindow.classList.contains("show")) {
    modalWindow.classList.add("show");
  }
  CopyPageLink();
});

// Delete Button
deleteBtn.addEventListener("click", function () {
  if (!modalWindow.classList.contains("show")) {
    modalWindow.classList.add("show");
  }

  DisplayModal(
    "",
    "Do you want to parmanently <br>delete this account?",
    "",
    true
  );
});

// Profile Button
profileBtn.addEventListener("click", function () {
  if (!profile.classList.contains("show-profile")) {
    profile.classList.add("show-profile");
  }
});

// Profile Close Button
closeBtn.addEventListener("click", function () {
  if (profile.classList.contains("show-profile")) {
    profile.classList.remove("show-profile");
  }
});

// Modal Window Close Button
modalCloseBtn.addEventListener("click", function () {
  if (modalWindow.classList.contains("show")) {
    modalWindow.classList.remove("show");
  }
});

// On Click, anywhere in the window.
window.onclick = function (event) {
  // If Modal window is active, close it.
  if (event.target == modalWindow) {
    if (modalWindow.classList.contains("show")) {
      modalWindow.classList.remove("show");
    }
  }
};

function CopyPageLink() {
  let url = window.location.href;
  navigator.clipboard.writeText(url);

  DisplayModal("", "URL Copied!!!<br>" + url, "", false);
}

function DisplayModal(headerText, bodyText, footerText, enableModalBtn) {
  let header = document
    .querySelector(".modal-header")
    .getElementsByTagName("h2")[0];
  header.innerHTML = headerText;

  let body = document.querySelector(".modal-body").getElementsByTagName("p")[0];
  body.innerHTML = bodyText;

  let footer = document
    .querySelector(".modal-footer")
    .getElementsByTagName("h3")[0];
  footer.innerHTML = footerText;

  let modalBtn = document.querySelector(".modal-btn");
  if (enableModalBtn) {
    if (!modalBtn.classList.contains("show")) {
      modalBtn.classList.add("show");
    }
  } else {
    if (modalBtn.classList.contains("show")) {
      modalBtn.classList.remove("show");
    }
  }
}
