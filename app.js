/* Vastra storefront interactions: cart, toast, newsletter, media swap-in */
(function () {
  "use strict";

  var count = parseInt(localStorage.getItem("vastra-cart") || "0", 10);
  var countEl = document.getElementById("cartCount");
  var toastEl = document.getElementById("toast");
  var toastTimer;

  function renderCount() { if (countEl) countEl.textContent = count; }
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("show"); }, 2200);
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".add-btn");
    if (!btn) return;
    count++;
    localStorage.setItem("vastra-cart", String(count));
    renderCount();
    toast((btn.dataset.name || "Item") + " added to your bag ✦");
  });

  var cartBtn = document.getElementById("cartBtn");
  if (cartBtn) cartBtn.addEventListener("click", function () {
    toast(count === 0 ? "Your bag is empty — go find your drape" :
      "Your bag: " + count + " piece" + (count > 1 ? "s" : "") + " · checkout coming soon");
  });

  window.vastraSubscribe = function (e) {
    e.preventDefault();
    var input = e.target.querySelector("input");
    toast("Welcome to the list, " + input.value.split("@")[0] + " ✦");
    input.value = "";
    return false;
  };

  // Swap SVG placeholders for generated photos when they exist (media/<name>.jpg)
  function trySwap(el, src, wrapSel) {
    var img = new Image();
    img.onload = function () {
      var holder = wrapSel ? el.querySelector(wrapSel) : el;
      holder.innerHTML = "";
      holder.appendChild(img);
    };
    img.src = src;
  }
  document.querySelectorAll(".cat-card[data-cat]").forEach(function (card) {
    trySwap(card, "media/cat-" + card.dataset.cat + ".jpg", ".thumb");
  });
  var kids = document.getElementById("kidsVisual");
  if (kids) trySwap(kids, "media/kids.jpg", null);

  renderCount();
})();
