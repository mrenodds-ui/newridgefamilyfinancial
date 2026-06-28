// NewRidgeFinancial 2.0 — mock pages only.
// Pure static viewer: shows the approved mockup images. No framework, no server.

const PAGES = [
  { id: "financial", label: "Financial dashboard", title: "Owner Financial Dashboard", image: "mockups/01-financial-dashboard.png" },
  { id: "softdent", label: "SoftDent", title: "SoftDent", image: "mockups/02-softdent.png" },
  { id: "quickbooks", label: "QuickBooks", title: "QuickBooks", image: "mockups/03-quickbooks.png" },
  { id: "ar", label: "A/R & Collections", title: "A/R & Collections", image: "mockups/04-ar-collections.png" },
  { id: "claims", label: "Claims Workbench", title: "Patient Claims Workbench", image: "mockups/05-claims-workbench.png" },
  { id: "narratives", label: "Insurance Narratives", title: "Insurance Narratives", image: "mockups/06-insurance-narratives.png" },
  { id: "documents", label: "Accounting Documents", title: "Accounting Documents", image: "mockups/07-accounting-documents.png" },
  { id: "library", label: "Document Library", title: "Document Library", image: "mockups/08-document-library.png" },
  { id: "hal", label: "HAL Command Center", title: "HAL Command Center", image: "mockups/09-hal-command-center.png" },
];

const nav = document.getElementById("nav");
const img = document.getElementById("mockImage");
const pageTitle = document.getElementById("pageTitle");
const buttons = {};

function select(id) {
  const page = PAGES.find((p) => p.id === id) || PAGES[0];
  img.src = page.image;
  img.alt = page.title + " mockup";
  pageTitle.textContent = page.title;
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

window.addEventListener("hashchange", () => {
  const id = window.location.hash.replace("#", "");
  if (id) select(id);
});

const initial = window.location.hash.replace("#", "") || PAGES[0].id;
select(initial);
