/** Helpers shared by the storefront and the admin dashboard. */

export const PLACEHOLDER = "/static/img/placeholder.png";

export function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char];
  });
}

/** Format an amount using the shop's currency label, e.g. "NPR 6,400". */
export function money(amount, currency = "NPR") {
  const rounded = Math.round(Number(amount ?? 0) * 100) / 100;
  const formatted = rounded.toLocaleString("en-IN", {
    minimumFractionDigits: rounded % 1 === 0 ? 0 : 2,
    maximumFractionDigits: 2,
  });
  return `${currency} ${formatted}`;
}

/** Serve uploads and static art through the Netlify Image CDN at the size actually needed. */
export function imageUrl(path, width, height) {
  return path || PLACEHOLDER;
}

/** Pre-filled WhatsApp order link containing the product name and price. */
export function whatsappOrderLink(settings, product) {
  const number = String(settings.whatsapp || "").replace(/\D/g, "");
  const lines = [`Hello ${settings.brandName || "there"}!`, ""];

  if (product) {
    lines.push(`I would like to order this item:`);
    lines.push(`*${product.name}* (${product.category})`);
    if (product.discountPercent > 0) {
      lines.push(
        `Price: ${money(product.finalPrice, settings.currency)} ` +
          `(${product.discountPercent}% off ${money(product.originalPrice, settings.currency)})`,
      );
    } else {
      lines.push(`Price: ${money(product.finalPrice, settings.currency)}`);
    }
    if (typeof location !== "undefined") {
      lines.push("", `${location.origin}/#/product/${product.id}`);
    }
  } else {
    lines.push("I have a question about your collection.");
  }

  return `https://wa.me/${number}?text=${encodeURIComponent(lines.join("\n"))}`;
}

export function telLink(settings) {
  return `tel:${String(settings.phone || "").replace(/[^\d+]/g, "")}`;
}

function cookie(name) { return document.cookie.split("; ").find(x => x.startsWith(name + "="))?.split("=").slice(1).join("=") || ""; }
export async function api(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const unsafe = !["GET", "HEAD", "OPTIONS"].includes(method);
  if (unsafe && !cookie("csrftoken")) await fetch("/api/session", { credentials: "same-origin" });
  const response = await fetch(path, {
    ...options,
    credentials: "same-origin",
    headers: { ...(options.body instanceof FormData ? {} : { "content-type": "application/json" }), ...(unsafe ? { "X-CSRFToken": decodeURIComponent(cookie("csrftoken")) } : {}), ...(options.headers || {}) },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}
