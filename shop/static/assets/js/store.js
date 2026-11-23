/**
 * Customer storefront. Everything rendered here comes from the database via
 * /api/products and /api/settings — nothing about the catalogue is hard-coded.
 */
import { api, escapeHtml, imageUrl, money, telLink, whatsappOrderLink } from "./shared.js";

const CATEGORY_ROUTES = {
  sarees: "Sarees",
  dresses: "Dresses",
  kurtis: "Kurtis",
  lehenga: "Lehenga",
  suits: "Suits",
  accessories: "Accessories",
};

const state = {
  settings: {},
  products: [],
  categories: [],
  counts: {},
  category: "All",
  search: "",
  sort: "newest",
  offersOnly: false,
  loaded: false,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

/* ---------------------------------------------------------------- settings */

function applySettings() {
  const s = state.settings;
  $$("[data-brand-name]").forEach((el) => (el.textContent = s.brandName || "Our Shop"));
  $$("[data-tagline]").forEach((el) => (el.textContent = s.tagline || ""));
  $$("[data-address]").forEach((el) => (el.textContent = s.address || ""));
  $$("[data-hours]").forEach((el) => (el.textContent = s.hours || ""));

  $$("[data-whatsapp]").forEach((el) => (el.href = whatsappOrderLink(s, null)));
  $$("[data-call]").forEach((el) => (el.href = telLink(s)));
  $$("[data-call-text]").forEach((el) => {
    el.href = telLink(s);
    el.textContent = s.phone || "";
  });
  $$("[data-email]").forEach((el) => {
    el.href = `mailto:${s.email || ""}`;
    el.textContent = s.email || "";
  });
  $$('[data-social="facebook"]').forEach((el) => (el.href = s.facebook || "#"));
  $$('[data-social="tiktok"]').forEach((el) => (el.href = s.tiktok || "#"));

  document.title = `${s.brandName || "Saree & Fashion"} — Sarees, Kurtis, Lehenga & Party Wear`;
}

/* ----------------------------------------------------------------- markup */

function priceBlock(product) {
  const currency = state.settings.currency || "NPR";
  if (product.discountPercent > 0) {
    return `
      <div class="prices">
        <span class="price-final">${money(product.finalPrice, currency)}</span>
        <span class="price-original">${money(product.originalPrice, currency)}</span>
        <span class="price-off">${product.discountPercent}% OFF</span>
      </div>`;
  }
  return `<div class="prices"><span class="price-final">${money(product.finalPrice, currency)}</span></div>`;
}

function cardMarkup(product) {
  const name = escapeHtml(product.name);
  return `
    <article class="card">
      <button class="card__media" data-open="${product.id}" aria-label="View ${name}">
        <img src="${imageUrl(product.imageUrl, 420, 525)}" alt="${name}" loading="lazy" />
        ${product.discountPercent > 0 ? `<span class="badge">${product.discountPercent}% off</span>` : ""}
        ${product.inStock ? "" : '<span class="badge badge--muted badge--right">Sold out</span>'}
      </button>
      <div class="card__body">
        <span class="card__cat">${escapeHtml(product.category)}</span>
        <h3 class="card__name"><a href="#/product/${product.id}">${name}</a></h3>
        ${priceBlock(product)}

        <div class="card__actions">
          <button class="btn btn--primary btn--sm"
                  data-cart="${product.id}"
                  ${product.inStock ? "" : "disabled"}>
            Add to Cart
          </button>

          <button class="btn btn--light btn--sm"
                  data-open="${product.id}">
            Details
          </button>
        </div>
      </div>
    </article>`;
}

function emptyState(message, hint) {
  return `
    <div class="state" style="grid-column:1/-1">
      <h3>${escapeHtml(message)}</h3>
      <p>${escapeHtml(hint)}</p>
      <a class="btn btn--primary" href="#/all">Browse everything</a>
    </div>`;
}

function skeletons(count = 8) {
  return `<div class="skeleton-grid" style="grid-column:1/-1">${'<div class="skeleton"></div>'.repeat(count)}</div>`;
}

/* --------------------------------------------------------------- filtering */

function normalizedCategory(value) {
  const name = String(value || "").trim().toLowerCase();
  if (["sari", "saree", "sarees", "saris"].includes(name)) return "sarees";
  if (["kurti", "kurtis", "kurta", "kurtas"].includes(name)) return "kurtis";
  return name;
}


function visibleProducts() {
  const term = state.search.trim().toLowerCase();
  let list = state.products.filter((product) => {
    if (state.offersOnly && product.discountPercent <= 0) return false;
    if (state.category !== "All" && normalizedCategory(product.category) !== normalizedCategory(state.category)) return false;
    if (!term) return true;
    return (
      product.name.toLowerCase().includes(term) ||
      product.category.toLowerCase().includes(term) ||
      (product.fabric || "").toLowerCase().includes(term) ||
      product.description.toLowerCase().includes(term)
    );
  });

  const sorters = {
    "price-asc": (a, b) => a.finalPrice - b.finalPrice,
    "price-desc": (a, b) => b.finalPrice - a.finalPrice,
    discount: (a, b) => b.discountPercent - a.discountPercent,
    newest: (a, b) => new Date(b.createdAt) - new Date(a.createdAt),
  };
  list = [...list].sort(sorters[state.sort] || sorters.newest);
  return list;
}

function renderChips() {
  const chips = $("#chips");
  if (!chips) return;
  const options = ["All", ...state.categories];
  chips.innerHTML = options
    .map((category) => {
      const count = category === "All" ? state.products.length : state.counts[category] || 0;
      return `<button class="chip" data-category="${escapeHtml(category)}" aria-pressed="${
        state.category === category
      }">${escapeHtml(category)} <span style="opacity:.6">(${count})</span></button>`;
    })
    .join("");
}

function renderShop() {
  const grid = $("#product-grid");
  if (!grid) return;

  if (!state.loaded) {
    grid.innerHTML = skeletons();
    $("#result-count").textContent = "";
    return;
  }

  const list = visibleProducts();
  renderChips();

  if (!list.length) {
    grid.innerHTML = state.products.length
      ? emptyState("Nothing matches that yet", "Try another search term or category — or message us on WhatsApp and we'll find it for you.")
      : emptyState("The collection is being added right now", "New pieces appear here the moment the shop owner uploads them from the dashboard.");
    $("#result-count").textContent = "";
    return;
  }

  grid.innerHTML = list.map(cardMarkup).join("");
  const label = state.offersOnly ? "item on offer" : "item";
  $("#result-count").textContent = `${list.length} ${label}${list.length === 1 ? "" : "s"}${
    state.category !== "All" ? ` in ${state.category}` : ""
  }${state.search ? ` matching “${state.search}”` : ""}`;
}

function renderFeatured() {
  const grid = $("#featured-grid");
  if (!grid) return;

  if (!state.loaded) {
    grid.innerHTML = skeletons(4);
    return;
  }
  const latest = [...state.products]
    .sort((a, b) => Number(b.featured) - Number(a.featured) || new Date(b.createdAt) - new Date(a.createdAt))
    .slice(0, 8);

  grid.innerHTML = latest.length
    ? latest.map(cardMarkup).join("")
    : `<div class="state" style="grid-column:1/-1">
         <h3>No products yet</h3>
         <p>The shop owner can add the first saree from the dashboard — it will show up here instantly, with its price and discount.</p>
         <a class="btn btn--primary" href="/admin">Open shop dashboard</a>
       </div>`;

  $$("[data-count]").forEach((el) => {
    const count = state.counts[el.dataset.count];
    if (count) el.textContent = `${count} piece${count === 1 ? "" : "s"} available`;
  });
}

/* ------------------------------------------------------------------ modal */

function openModal(id) {
  const product = state.products.find((item) => String(item.id) === String(id));
  const modal = $("#modal");
  if (!product) return;

  const currency = state.settings.currency || "NPR";
  const discountRow =
    product.discountPercent > 0
      ? `<div><dt>You save</dt><dd style="color:var(--green)">${money(product.savings, currency)} (${product.discountPercent}%)</dd></div>`
      : "";

  $("#modal-content").innerHTML = `
    <div class="modal__media">
      <img src="${imageUrl(product.imageUrl, 700, 875)}" alt="${escapeHtml(product.name)}" />
    </div>
    <div class="modal__body">
      <span class="card__cat">${escapeHtml(product.category)}</span>
      <h2 id="modal-title">${escapeHtml(product.name)}</h2>
      ${priceBlock(product)}
      <p class="modal__desc">${escapeHtml(product.description || "Message us on WhatsApp for more details, fabric information and delivery time.")}</p>
      <dl class="meta-list">
        <div><dt>Original price</dt><dd>${money(product.originalPrice, currency)}</dd></div>
        ${discountRow}
        <div><dt>Final price</dt><dd style="color:var(--crimson);font-weight:600">${money(product.finalPrice, currency)}</dd></div>
        ${product.fabric ? `<div><dt>Fabric</dt><dd>${escapeHtml(product.fabric)}</dd></div>` : ""}
        <div><dt>Availability</dt><dd>${product.inStock ? "In stock" : "Sold out — ask for restock"}</dd></div>
      </dl>
      <div class="modal__actions">
        <a class="btn btn--whatsapp btn--block" href="${whatsappOrderLink(state.settings, product)}" target="_blank" rel="noopener">Order on WhatsApp</a>
        <a class="btn btn--primary btn--block" href="${telLink(state.settings)}">Call to order</a>
      </div>
    </div>`;

  modal.hidden = false;
  modal.classList.add("is-open");
  document.body.style.overflow = "hidden";
  $("#modal-close").focus();
}

function closeModal({ updateHash = true } = {}) {
  const modal = $("#modal");
  modal.classList.remove("is-open");
  modal.hidden = true;
  document.body.style.overflow = "";
  if (updateHash && location.hash.startsWith("#/product/")) {
    history.replaceState(null, "", "#/all");
    route();
  }
}

/* ----------------------------------------------------------------- router */

function showView(name) {
  $$(".view").forEach((view) => (view.hidden = view.dataset.view !== name));
}

function markNav(hash) {
  $$("#nav a").forEach((link) => {
    if (link.getAttribute("href") === hash) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
}

async function loadCart() {
  const data = await api("/api/cart/");
  const box = $("#cart-items");

  if (!data.items.length) {
    box.innerHTML = "<p>Your cart is empty.</p>";
    $("#cart-total").textContent = "0";
    return;
  }

  let total = 0;

  box.innerHTML = data.items.map(item => {
    total += item.total;

    return `
      <div style="display:flex;gap:20px;align-items:center;margin-bottom:20px;">
        ${item.imageUrl
          ? `<img src="${item.imageUrl}" width="80" height="100"
                  style="object-fit:cover;border-radius:8px;">`
          : ""}

        <div style="flex:1;">
          <strong>${escapeHtml(item.name)}</strong>
          <p>NPR ${item.price}</p>

          <div style="display:flex; align-items:center; gap:10px; margin-top:10px;">

            <button
              class="btn btn--light btn--sm"
              data-cart-minus="${item.id}"
              data-quantity="${item.quantity}">
              −
            </button>

            <strong>${item.quantity}</strong>

            <button
              class="btn btn--light btn--sm"
              data-cart-plus="${item.id}"
              data-quantity="${item.quantity}">
              +
            </button>

            <button
              class="btn btn--light btn--sm"
              data-cart-remove="${item.id}">
              Remove
            </button>

          </div>
        </div>

        <strong>NPR ${item.total}</strong>
      </div>
    `;
  }).join("");

  $("#cart-total").textContent = total.toFixed(2);
}

async function loadCheckout() {
  const data = await api("/api/cart/");

  let total = 0;

  data.items.forEach(item => {
    total += item.total;
  });

  $("#checkout-total").textContent = total.toFixed(2);
}

async function verifyPayment(orderId) {
  try {
    const result = await api(`/api/esewa/verify/${orderId}/`);

    if (result.verified) {
      alert("Payment successful!");
      window.location.hash = "#/";
    } else {
      alert("Payment verification failed.");
    }
  } catch (error) {
    alert(error.message);
  }
}

function route() {
  const hash = location.hash || "#/";
  const segments = hash.replace(/^#\/?/, "").split("/").filter(Boolean);
  const [first, second] = segments;

  if (first === "product" && second) {
    showView("shop");
    state.offersOnly = false;
    state.category = "All";
    renderShop();
    markNav("#/all");
    if (state.loaded) openModal(second);
    return;
  }

  closeModal({ updateHash: false });

  if (!first) {
    showView("home");
    markNav("#/");
    renderFeatured();
    window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
    return;
  }

  if (first === "checkout") {
    showView("checkout");
    loadCheckout();
    return;
  }

  if (first === "payment-success" && second) {
    const orderId = second;
    showView("checkout");
    verifyPayment(orderId);
    return;
  }

  if (first === "cart") {
    showView("cart");
    loadCart();
    return;
  }

  if (first === "contact") {
    showView("contact");
    markNav("#/contact");
    window.scrollTo({ top: 0, behavior: "auto" });
    return;
  }

  showView("shop");
  state.offersOnly = first === "offers";
  state.category = CATEGORY_ROUTES[first] || "All";

  const heading = state.offersOnly
    ? { eyebrow: "Limited time", title: "Today's offers", subtitle: "Every discounted piece in the shop, sorted by the biggest saving." }
    : state.category === "All"
      ? { eyebrow: "Collection", title: "All products", subtitle: "Search, filter and order any piece straight from WhatsApp." }
      : {
          eyebrow: "Collection",
          title: state.category,
          subtitle: `Our current ${state.category.toLowerCase()} — tap any piece for full details and pricing.`,
        };

  $("#shop-eyebrow").textContent = heading.eyebrow;
  $("#shop-title").textContent = heading.title;
  $("#shop-subtitle").textContent = heading.subtitle;

  if (state.offersOnly) {
    state.sort = "discount";
    if ($("#sort")) $("#sort").value = "discount";
  }

  markNav(state.offersOnly ? "#/offers" : `#/${first}`);
  renderShop();
  window.scrollTo({ top: 0, behavior: "auto" });
}

/* ------------------------------------------------------------------- boot */

function wireEvents() {
  const burger = $("#burger");
  const nav = $("#nav");
  if (burger) {
  burger.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    burger.setAttribute("aria-expanded", String(open));
  });
}

nav.addEventListener("click", (event) => {
  if (event.target.closest("a")) {
    nav.classList.remove("is-open");

    if (burger) {
      burger.setAttribute("aria-expanded", "false");
    }
  }
});

  $("#search")?.addEventListener("input", (event) => {
  state.search = event.target.value;
  renderShop();
});

$("#sort")?.addEventListener("change", (event) => {
  state.sort = event.target.value;
  renderShop();
});

$("#chips")?.addEventListener("click", (event) => {
  const chip = event.target.closest("[data-category]");
  if (!chip) return;

  state.category = chip.dataset.category;
  renderChips();
  renderShop();
});

  document.addEventListener("click", (event) => {
    const opener = event.target.closest("[data-open]");
    if (opener) {
      event.preventDefault();
      location.hash = `#/product/${opener.dataset.open}`;
    }
  });

  $("#modal-close").addEventListener("click", () => closeModal());
  $("#modal").addEventListener("click", (event) => {
    if (event.target === $("#modal")) closeModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && $("#modal").classList.contains("is-open")) closeModal();
  });

  window.addEventListener("hashchange", route);
}

async function load() {
  const cart = await api("/api/cart/");
  $("#cart-count").textContent =
    cart.items.reduce((total, item) => total + item.quantity, 0);

  const [settingsResponse, productsResponse] = await Promise.allSettled([
    api("/api/settings"),
    api("/api/products"),
  ]);

  if (settingsResponse.status === "fulfilled") {
    state.settings = settingsResponse.value.settings;
    applySettings();
  }

  if (productsResponse.status === "fulfilled") {
    state.products = productsResponse.value.products;
    state.categories = productsResponse.value.categories;
    state.counts = productsResponse.value.counts;
  } else {
    console.error(productsResponse.reason);
  }

  state.loaded = true;
  route();
}

document.addEventListener("click", async (event) => {

  const plus = event.target.closest("[data-cart-plus]");
  const minus = event.target.closest("[data-cart-minus]");
  const remove = event.target.closest("[data-cart-remove]");

  if (plus) {
    const id = plus.dataset.cartPlus;
    const quantity = Number(plus.dataset.quantity) + 1;

    const result = await api(`/api/cart/update/${id}/`, {
      method: "POST",
      body: JSON.stringify({ quantity })
    });

    $("#cart-count").textContent = result.cartCount;
    await loadCart();
    return;
  }

  if (minus) {
    const id = minus.dataset.cartMinus;
    const quantity = Number(minus.dataset.quantity) - 1;

    const result = await api(`/api/cart/update/${id}/`, {
      method: "POST",
      body: JSON.stringify({ quantity })
    });

    $("#cart-count").textContent = result.cartCount;
    await loadCart();
    return;
  }

  if (remove) {
    const id = remove.dataset.cartRemove;

    const result = await api(`/api/cart/remove/${id}/`, {
      method: "POST"
    });

    $("#cart-count").textContent = result.cartCount;
    await loadCart();
  }

});

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-cart]");
  if (!button) return;

  try {
    const result = await api(
      `/api/cart/add/${button.dataset.cart}/`,
      { method: "POST" }
    );

    button.textContent = "✓ Added";

    setTimeout(() => {
      button.textContent = "Add to Cart";
    }, 1200);

    $("#cart-count").textContent = result.cartCount;

  } catch (error) {
    alert(error.message);
  }
});

$("#checkout-btn")?.addEventListener("click", () => {
  window.location.hash = "#/checkout";
});

$("#checkout-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();

  try {
    // 1. Create order
    const order = await api("/api/orders/create/", {
      method: "POST",
      body: JSON.stringify({
        name: $("#customer-name").value,
        phone: $("#customer-phone").value,
        address: $("#customer-address").value
      })
    });

    // 2. Get eSewa payment data
    const payment = await api(`/api/esewa/payment/${order.orderId}/`, {
      method: "POST"
    });

    // 3. Submit payment to eSewa
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "https://rc-epay.esewa.com.np/api/epay/main/v2/form";

    const fields = {
      amount: payment.amount,
      tax_amount: "0",
      total_amount: payment.total_amount,
      transaction_uuid: payment.transaction_uuid,
      product_code: payment.product_code,
      product_service_charge: "0",
      product_delivery_charge: "0",
      success_url: `${location.origin}/payment/esewa/success/${order.orderId}/`,
      failure_url: `${location.origin}/#/payment-failed/${order.orderId}`,
      signed_field_names: payment.signed_field_names,
      signature: payment.signature
    };

    for (const [name, value] of Object.entries(fields)) {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = name;
      input.value = value;
      form.appendChild(input);
    }

    document.body.appendChild(form);
    form.submit();

  } catch (error) {
    alert(error.message);
  }
});

$("#year").textContent = new Date().getFullYear();
wireEvents();
route();
load();
// Product filter dropdown
const productBtn = document.getElementById("product-filter-btn");
const productMenu = document.getElementById("product-filter-menu");

if (productBtn && productMenu) {
  productBtn.addEventListener("click", (event) => {
    event.stopPropagation();
    productMenu.hidden = !productMenu.hidden;
  });

  productMenu.addEventListener("click", () => {
    productMenu.hidden = true;
  });

  document.addEventListener("click", () => {
    productMenu.hidden = true;
  });
}


// Header product search
const searchButton = document.getElementById("search-button");
const headerSearch = document.getElementById("header-search-input");
const header = document.querySelector(".header");

if (searchButton && headerSearch && header) {
  searchButton.addEventListener("click", () => {
    header.classList.add("search-mode");
    headerSearch.hidden = false;
    headerSearch.focus();
  });

  headerSearch.addEventListener("input", (event) => {
    state.search = event.target.value;

    if (location.hash !== "#/all") {
      location.hash = "#/all";
    } else {
      renderShop();
    }
  });

  headerSearch.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      header.classList.remove("search-mode");
      headerSearch.hidden = true;
      headerSearch.value = "";
      state.search = "";
      renderShop();
    }
  });
}


// Close search when empty and clicking outside
document.addEventListener("click", (event) => {
  if (!header || !headerSearch) return;

  const clickedSearch = event.target.closest(".header-search");

  if (
    header.classList.contains("search-mode") &&
    !clickedSearch &&
    headerSearch.value.trim() === ""
  ) {
    header.classList.remove("search-mode");
    headerSearch.hidden = true;
  }
});


// Price filter dropdown
const priceBtn = document.getElementById("price-filter-btn");
const priceMenu = document.getElementById("price-filter-menu");

if (priceBtn && priceMenu) {
  priceBtn.addEventListener("click", (event) => {
    event.stopPropagation();

    // Close product dropdown
    if (productMenu) productMenu.hidden = true;

    priceMenu.hidden = !priceMenu.hidden;
  });

  priceMenu.addEventListener("click", (event) => {
    const option = event.target.closest("[data-sort]");
    if (!option) return;

    state.sort = option.dataset.sort;
    priceMenu.hidden = true;

    if (location.hash !== "#/all") {
      location.hash = "#/all";
    } else {
      renderShop();
    }
  });

  document.addEventListener("click", (event) => {
    if (!event.target.closest("#price-filter-menu") &&
        !event.target.closest("#price-filter-btn")) {
      priceMenu.hidden = true;
    }
  });
}
