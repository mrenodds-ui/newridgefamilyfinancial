// NewRidgeFinancial 2.0 — mission-control pages.

const PAGES = [
  { id: "financial", label: "Financial dashboard", title: "Owner Financial Dashboard", image: "pages/01-financial-dashboard.png" },
  { id: "softdent", label: "SoftDent", title: "SoftDent", image: "pages/02-softdent.png" },
  { id: "quickbooks", label: "QuickBooks", title: "QuickBooks", image: "pages/03-quickbooks.png" },
  { id: "ar", label: "A/R & Collections", title: "A/R & Collections", image: "pages/04-ar-collections.png" },
  { id: "claims", label: "Claims Workbench", title: "Patient Claims Workbench", image: "pages/05-claims-workbench.png" },
  { id: "narratives", label: "Insurance Narratives", title: "Insurance Narratives", image: "pages/06-insurance-narratives.png" },
  { id: "documents", label: "Accounting Documents", title: "Accounting Documents", image: "pages/07-accounting-documents.png" },
  { id: "library", label: "Document Library", title: "Document Library", image: "pages/08-document-library.png" },
  { id: "hal", label: "HAL Command Center", title: "HAL Command Center", image: "pages/09-hal-command-center.png" },
];

const FALLBACK_HAL = {
  status: {
    title: "HAL Command Center",
    summary: "Local program manager for NewRidgeFinancial 2.0.",
    posture: ["Local-only", "Read-only", "Human review required", "Not submitted"],
    modelLanes: [
      { name: "14B chat lane", role: "Staff-facing conversation", state: "Planned" },
      { name: "21B reasoning lane", role: "Program review and prioritization", state: "Planned" },
      { name: "30B escalation lane", role: "Second-opinion review", state: "Planned" },
    ],
  },
  askHal: {
    title: "Ask HAL",
    summary: "HAL is currently operating as a local program manager.",
    suggestions: ["Show priorities", "Open claims", "Review source health"],
    response: "I can navigate pages, explain local status, and keep work inside the read-only boundary.",
  },
  sources: { title: "Read-only source intake", summary: "Source pages are read-only.", items: [] },
  reasoning: { title: "Local reasoning core", summary: "Organizes work into Ready, Needs review, and Blocked lanes.", lanes: [] },
  workSurfaces: { title: "Staff work surfaces", summary: "Open and explain each program surface.", items: [] },
  firewall: { title: "External action firewall", summary: "External actions are blocked by design.", blocked: [], allowed: [] },
  priorities: { title: "Today’s operator priorities", items: [] },
};

const HOTSPOTS = [
  { key: "askHal", label: "Ask HAL", left: 15, top: 15, width: 45, height: 17 },
  { key: "sources", label: "Source intake", left: 8, top: 37, width: 25, height: 34 },
  { key: "reasoning", label: "Reasoning core", left: 36, top: 37, width: 28, height: 34 },
  { key: "workSurfaces", label: "Work surfaces", left: 67, top: 37, width: 27, height: 34 },
  { key: "firewall", label: "External firewall", left: 9, top: 76, width: 84, height: 15 },
  { key: "priorities", label: "Priorities", left: 66, top: 13, width: 28, height: 19 },
];

const nav = document.getElementById("nav");
const img = document.getElementById("pageImage");
const pageTitle = document.getElementById("pageTitle");
const hotspotLayer = document.getElementById("hotspotLayer");
const drawer = document.getElementById("drawer");
const drawerClose = document.getElementById("drawerClose");
const drawerTitle = document.getElementById("drawerTitle");
const drawerContent = document.getElementById("drawerContent");
const buttons = {};
let halData = FALLBACK_HAL;

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function cards(items) {
  if (!items || items.length === 0) return "";
  return `<div class="drawer-grid">${items
    .map(
      (item) => `<div class="drawer-card"><strong>${escapeHtml(item.label || item.name)}</strong>${escapeHtml(
        item.detail || item.role || item.state || "",
      )}</div>`,
    )
    .join("")}</div>`;
}

function chips(items, blocked = false) {
  if (!items || items.length === 0) return "";
  return `<div>${items
    .map((item) => `<span class="status-chip${blocked ? " status-chip--blocked" : ""}">${escapeHtml(item)}</span>`)
    .join("")}</div>`;
}

function numbered(items) {
  if (!items || items.length === 0) return "";
  return `<div class="drawer-grid">${items.map((item) => `<div class="drawer-card">${escapeHtml(item)}</div>`).join("")}</div>`;
}

function surfaceActions(items) {
  if (!items || items.length === 0) return "";
  return `<div class="drawer-grid">${items
    .map(
      (item) =>
        `<button class="drawer-action" type="button" data-target-page="${escapeHtml(item.target)}"><strong>${escapeHtml(
          item.label,
        )}</strong>${escapeHtml(item.detail)}</button>`,
    )
    .join("")}</div>`;
}

function renderPanel(key) {
  const data = halData[key] || halData.status;
  drawerTitle.textContent = data.title || "HAL Command Center";

  if (key === "askHal") {
    drawerContent.innerHTML = `
      <p>${escapeHtml(data.summary)}</p>
      ${chips(data.suggestions)}
      <div class="drawer-card"><strong>HAL response</strong>${escapeHtml(data.response)}</div>
    `;
    return;
  }

  if (key === "status") {
    drawerContent.innerHTML = `
      <p>${escapeHtml(data.summary)}</p>
      ${chips(data.posture)}
      ${cards(data.modelLanes)}
    `;
    return;
  }

  if (key === "reasoning") {
    drawerContent.innerHTML = `
      <p>${escapeHtml(data.summary)}</p>
      ${cards(data.lanes)}
    `;
    return;
  }

  if (key === "workSurfaces") {
    drawerContent.innerHTML = `
      <p>${escapeHtml(data.summary)}</p>
      ${surfaceActions(data.items)}
    `;
    drawerContent.querySelectorAll("[data-target-page]").forEach((button) => {
      button.addEventListener("click", () => {
        closeDrawer();
        select(button.dataset.targetPage);
      });
    });
    return;
  }

  if (key === "firewall") {
    drawerContent.innerHTML = `
      <p>${escapeHtml(data.summary)}</p>
      <div><strong>Blocked</strong>${chips(data.blocked, true)}</div>
      <div><strong>Allowed</strong>${chips(data.allowed)}</div>
    `;
    return;
  }

  if (key === "priorities") {
    drawerContent.innerHTML = numbered(data.items);
    return;
  }

  drawerContent.innerHTML = `
    <p>${escapeHtml(data.summary)}</p>
    ${cards(data.items)}
  `;
}

function openDrawer(key) {
  renderPanel(key);
  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
}

function closeDrawer() {
  drawer.classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
}

function renderHotspots(pageId) {
  hotspotLayer.innerHTML = "";
  hotspotLayer.classList.toggle("active", pageId === "hal");
  if (pageId !== "hal") return;

  for (const hotspot of HOTSPOTS) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "hotspot";
    button.setAttribute("aria-label", hotspot.label);
    button.style.left = `${hotspot.left}%`;
    button.style.top = `${hotspot.top}%`;
    button.style.width = `${hotspot.width}%`;
    button.style.height = `${hotspot.height}%`;
    button.addEventListener("click", () => openDrawer(hotspot.key));
    hotspotLayer.appendChild(button);
  }
}

function select(id) {
  const page = PAGES.find((p) => p.id === id) || PAGES[0];
  img.src = page.image;
  img.alt = page.title;
  pageTitle.textContent = page.title;
  renderHotspots(page.id);
  closeDrawer();
  for (const key of Object.keys(buttons)) {
    buttons[key].classList.toggle("active", key === page.id);
  }
  if (window.location.hash !== "#" + page.id) {
    window.location.hash = page.id;
  }
}

for (const page of PAGES) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.textContent = page.label;
  btn.addEventListener("click", () => select(page.id));
  nav.appendChild(btn);
  buttons[page.id] = btn;
}

drawerClose.addEventListener("click", closeDrawer);
drawer.addEventListener("click", (event) => {
  if (event.target === drawer) closeDrawer();
});
window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeDrawer();
});
window.addEventListener("hashchange", () => {
  const id = window.location.hash.replace("#", "");
  if (id) select(id);
});

fetch("data/hal-manager.json", { cache: "no-store" })
  .then((response) => {
    if (!response.ok) throw new Error("HAL data unavailable");
    return response.json();
  })
  .then((data) => {
    halData = data;
  })
  .catch(() => {
    halData = FALLBACK_HAL;
  });

const initial = window.location.hash.replace("#", "") || PAGES[0].id;
select(initial);
