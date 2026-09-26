/**
 * Shop owner dashboard. Handles sign-in, product CRUD, photo uploads from the
 * owner's device, and the editable shop contact details.
 */
import { api, escapeHtml, imageUrl, money } from "./shared.js";

const state = {
  products: [],
  categories: [],
  settings: {},
  filter: "",
  editingId: null,
  pendingFile: null,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

/* ------------------------------------------------------------------ toasts */

function toast(message, kind = "ok") {
  const el = document.createElement("div");
  el.className = `toast toast--${kind}`;
  el.textContent = message;
  $("#toasts").append(el);
  setTimeout(() => el.remove(), 3800);
}

function showError(target, message) {
  const el = $(target);
  el.textContent = message;
  el.hidden = !message;
}

/* -------------------------------------------------------------------- auth */

async function checkSession() {
  const { authenticated, defaultPassword } = await api("/api/session");
  $("#login").hidden = authenticated;
  $("#dashboard").hidden = !authenticated;
  $("#password-warning").hidden = !(authenticated && defaultPassword);
  if (authenticated) await loadAll();
  else $("#password").focus();
}

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  showError("#login-error", "");
  const button = $("#login-btn");
  button.disabled = true;
  button.textContent = "Signing in…";
  try {
    await api("/api/login", { method: "POST", body: JSON.stringify({ password: $("#password").value }) });
    $("#password").value = "";
    await checkSession();
  } catch (error) {
    showError("#login-error", error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Sign in";
  }
});

$("#logout").addEventListener("click", async () => {
  await api("/api/logout", { method: "POST" }).catch(() => {});
  location.reload();
});

/* -------------------------------------------------------------------- tabs */

function openTab(name) {
  $$(".tab").forEach((tab) => tab.setAttribute("aria-selected", String(tab.dataset.tab === name)));
  $$("[data-panel]").forEach((panel) => (panel.hidden = panel.dataset.panel !== name));
  window.scrollTo({ top: 0, behavior: "auto" });
}

$$(".tab").forEach((tab) => tab.addEventListener("click", () => openTab(tab.dataset.tab)));
$$("[data-goto-add]").forEach((button) =>
  button.addEventListener("click", () => {
    resetForm();
    openTab("add");
  }),
);

/* ------------------------------------------------------------------ loading */

async function loadAll() {
  await Promise.all([loadProducts(), loadSettings()]);
}

async function loadProducts() {
  try {
    const { products, categories } = await api("/api/products");
    state.products = products;
    state.categories = categories;
    fillCategorySelect();
    renderStats();
    renderRows();
  } catch (error) {
    toast(error.message, "err");
    $("#rows").innerHTML = `<tr><td colspan="8" class="empty">Could not load products. ${escapeHtml(error.message)}</td></tr>`;
  }
}

async function loadSettings() {
  try {
    const { settings } = await api("/api/settings");
    state.settings = settings;
    Object.entries(settings).forEach(([key, value]) => {
      const input = document.getElementById(key);
      if (input) input.value = value;
    });
    $("#brand-label").textContent = settings.brandName || "Saree & Fashion";
  } catch (error) {
    toast(error.message, "err");
  }
}

function fillCategorySelect() {
  const select = $("#category");
  const current = select.value;
  select.innerHTML = state.categories
    .map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)}</option>`)
    .join("");
  if (current) select.value = current;
}

/* ----------------------------------------------------------------- rendering */

function renderStats() {
  const currency = state.settings.currency || "NPR";
  const onOffer = state.products.filter((product) => product.discountPercent > 0).length;
  const outOfStock = state.products.filter((product) => !product.inStock).length;
  const inventoryValue = state.products.reduce((total, product) => total + product.finalPrice, 0);

  $("#stats").innerHTML = [
    ["Products live", state.products.length],
    ["On offer", onOffer],
    ["Sold out", outOfStock],
    ["Catalogue value", money(inventoryValue, currency)],
  ]
    .map(([label, value]) => `<div class="stat"><b>${escapeHtml(String(value))}</b><span>${label}</span></div>`)
    .join("");
}

function renderRows() {
  const currency = state.settings.currency || "NPR";
  const term = state.filter.trim().toLowerCase();
  const rows = state.products.filter(
    (product) =>
      !term ||
      product.name.toLowerCase().includes(term) ||
      product.category.toLowerCase().includes(term),
  );

  if (!rows.length) {
    $("#rows").innerHTML = `<tr><td colspan="8" class="empty">${
      state.products.length
        ? "No products match that search."
        : "No products yet — add your first saree using the “Add product” tab."
    }</td></tr>`;
    return;
  }

  $("#rows").innerHTML = rows
    .map(
      (product) => `
        <tr>
          <td><img class="thumb" src="${imageUrl(product.imageUrl, 108, 136)}" alt="" /></td>
          <td class="row-name">${escapeHtml(product.name)}${
            product.featured ? '<small>★ Featured on home page</small>' : ""
          }${product.fabric ? `<small>${escapeHtml(product.fabric)}</small>` : ""}</td>
          <td><span class="pill">${escapeHtml(product.category)}</span></td>
          <td>${money(product.originalPrice, currency)}</td>
          <td>${
            product.discountPercent > 0
              ? `<span class="pill pill--off">${product.discountPercent}% off</span>`
              : "—"
          }</td>
          <td><strong>${money(product.finalPrice, currency)}</strong></td>
          <td>${
            product.inStock
              ? '<span class="pill pill--off">In stock</span>'
              : '<span class="pill pill--out">Sold out</span>'
          }</td>
          <td>
            <div class="row-actions">
              <button class="btn btn--outline btn--sm" data-edit="${product.id}">Edit</button>
              <button class="btn btn--danger btn--sm" data-delete="${product.id}">Delete</button>
            </div>
          </td>
        </tr>`,
    )
    .join("");
}

$("#filter").addEventListener("input", (event) => {
  state.filter = event.target.value;
  renderRows();
});

$("#rows").addEventListener("click", (event) => {
  const edit = event.target.closest("[data-edit]");
  const remove = event.target.closest("[data-delete]");
  if (edit) startEdit(Number(edit.dataset.edit));
  if (remove) deleteProduct(Number(remove.dataset.delete));
});

/* --------------------------------------------------------------- price math */

function updatePricePreview() {
  const currency = state.settings.currency || "NPR";
  const original = Number($("#original-price").value);
  const discount = Math.min(99, Math.max(0, Number($("#discount").value) || 0));

  if (!Number.isFinite(original) || original <= 0) {
    $("#preview-final").textContent = "—";
    $("#preview-original").textContent = "";
    $("#preview-off").textContent = "";
    return;
  }

  const final = Math.round(original * (1 - discount / 100) * 100) / 100;
  $("#preview-final").textContent = money(final, currency);
  $("#preview-original").textContent = discount > 0 ? money(original, currency) : "";
  $("#preview-off").textContent = discount > 0 ? `${discount}% OFF · saves ${money(original - final, currency)}` : "";
}

$("#original-price").addEventListener("input", updatePricePreview);
$("#discount").addEventListener("input", updatePricePreview);

/* ------------------------------------------------------------ image picking */

function setPreview(source, label = "No photo yet") {
  $("#preview").innerHTML = source ? `<img src="${source}" alt="Product preview" />` : label;
  $("#remove-image").hidden = !source;
}

$("#pick-image").addEventListener("click", () => $("#image-file").click());

$("#image-file").addEventListener("change", (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  if (file.size > 8 * 1024 * 1024) {
    toast("That photo is larger than 8 MB. Please choose a smaller one.", "err");
    event.target.value = "";
    return;
  }
  state.pendingFile = file;
  setPreview(URL.createObjectURL(file));
});

$("#remove-image").addEventListener("click", () => {
  state.pendingFile = null;
  $("#image-file").value = "";
  $("#image-key").value = "";
  setPreview(null);
});

/* --------------------------------------------------------------- product form */

function resetForm() {
  state.editingId = null;
  state.pendingFile = null;
  $("#product-form").reset();
  $("#product-id").value = "";
  $("#image-key").value = "";
  $("#image-file").value = "";
  $("#in-stock").checked = true;
  $("#discount").value = 0;
  setPreview(null);
  updatePricePreview();
  showError("#form-error", "");
  $("#form-title").textContent = "Add a new product";
  $("#form-hint").textContent =
    "Upload a photo from your computer or phone, set the price and discount — the final price is calculated for you.";
  $("#save-btn").textContent = "Save product";
  $("#delete-btn").hidden = true;
}

function startEdit(id) {
  const product = state.products.find((item) => item.id === id);
  if (!product) return;

  state.editingId = id;
  state.pendingFile = null;
  $("#product-id").value = id;
  $("#name").value = product.name;
  $("#category").value = product.category;
  $("#fabric").value = product.fabric || "";
  $("#original-price").value = product.originalPrice;
  $("#discount").value = product.discountPercent;
  $("#description").value = product.description || "";
  $("#in-stock").checked = product.inStock;
  $("#featured").checked = product.featured;
  $("#image-key").value = product.imageKey || "";
  $("#image-file").value = "";
  setPreview(product.imageUrl ? imageUrl(product.imageUrl, 216, 270) : null);
  updatePricePreview();
  showError("#form-error", "");

  $("#form-title").textContent = `Edit “${product.name}”`;
  $("#form-hint").textContent = "Change the photo, price or discount — the shop updates as soon as you save.";
  $("#save-btn").textContent = "Update product";
  $("#delete-btn").hidden = false;
  openTab("add");
}

async function uploadPendingImage() {
  if (!state.pendingFile) return $("#image-key").value || null;
  const body = new FormData();
  body.append("image", state.pendingFile);
  const { imageKey } = await api("/api/upload", { method: "POST", body });
  return imageKey;
}

$("#product-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  showError("#form-error", "");

  const button = $("#save-btn");
  const label = button.textContent;
  button.disabled = true;
  button.textContent = state.pendingFile ? "Uploading photo…" : "Saving…";

  try {
    const imageKey = await uploadPendingImage();
    const payload = {
      name: $("#name").value,
      category: $("#category").value,
      fabric: $("#fabric").value,
      originalPrice: $("#original-price").value,
      discountPercent: Number($("#discount").value) || 0,
      description: $("#description").value,
      inStock: $("#in-stock").checked,
      featured: $("#featured").checked,
      imageKey,
    };

    if (state.editingId) {
      await api(`/api/products/${state.editingId}`, { method: "PUT", body: JSON.stringify(payload) });
      toast("Product updated — the shop is already showing it.");
    } else {
      await api("/api/products", { method: "POST", body: JSON.stringify(payload) });
      toast("Product added — it is live on the shop now.");
    }

    resetForm();
    await loadProducts();
    openTab("products");
  } catch (error) {
    showError("#form-error", error.message);
    toast(error.message, "err");
  } finally {
    button.disabled = false;
    button.textContent = label;
  }
});

$("#reset-btn").addEventListener("click", resetForm);

async function deleteProduct(id) {
  const product = state.products.find((item) => item.id === id);
  if (!product) return;
  if (!confirm(`Delete “${product.name}”? This removes it from the shop and cannot be undone.`)) return;

  try {
    await api(`/api/products/${id}`, { method: "DELETE" });
    toast("Product deleted.");
    if (state.editingId === id) resetForm();
    await loadProducts();
  } catch (error) {
    toast(error.message, "err");
  }
}

$("#delete-btn").addEventListener("click", () => {
  if (state.editingId) deleteProduct(state.editingId);
});

/* ------------------------------------------------------------------ settings */

$("#settings-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  showError("#settings-error", "");
  const button = $("#settings-btn");
  button.disabled = true;
  button.textContent = "Saving…";

  const payload = {};
  Object.keys(state.settings).forEach((key) => {
    const input = document.getElementById(key);
    if (input) payload[key] = input.value;
  });

  try {
    const { settings } = await api("/api/settings", { method: "PUT", body: JSON.stringify(payload) });
    state.settings = settings;
    $("#brand-label").textContent = settings.brandName || "Saree & Fashion";
    renderStats();
    renderRows();
    toast("Shop settings saved.");
  } catch (error) {
    showError("#settings-error", error.message);
    toast(error.message, "err");
  } finally {
    button.disabled = false;
    button.textContent = "Save settings";
  }
});

/* ---------------------------------------------------------------------- boot */

checkSession().catch((error) => {
  $("#login").hidden = false;
  showError("#login-error", error.message);
});
