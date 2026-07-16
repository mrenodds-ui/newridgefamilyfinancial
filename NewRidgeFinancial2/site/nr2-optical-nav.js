(() => {
  const pages = [
    { href: "/nr2-optical-beam-touch-mockup.html", label: "MAIN · LANDING", crumb: "Landing" },
    { href: "/nr2-optical-pages-hub.html", label: "ALIGNMENT BENCH", crumb: "Alignment Bench" },
    { group: "SOURCES" },
    { href: "/nr2-optical-page-softdent.html", label: "SoftDent", crumb: "SoftDent" },
    { href: "/nr2-optical-page-quickbooks.html", label: "QuickBooks", crumb: "QuickBooks" },
    { href: "/nr2-optical-page-ar.html", label: "A/R Aging", crumb: "A/R Aging" },
    { group: "HAL" },
    { href: "/nr2-optical-page-hal.html", label: "HAL + Chat", crumb: "HAL" },
    { href: "/nr2-optical-page-claims.html", label: "Claims + ERA", crumb: "Claims" },
    { href: "/nr2-optical-page-narratives.html", label: "Narratives", crumb: "Narratives" },
    { href: "/nr2-optical-page-analytics.html", label: "Analytics / Huddle", crumb: "Analytics" },
    { group: "PLANNING" },
    { href: "/nr2-optical-page-taxes.html", label: "Taxes", crumb: "Taxes" },
    { href: "/nr2-optical-page-office-manager.html", label: "Office Manager", crumb: "Office Manager" },
    { href: "/nr2-optical-page-content.html", label: "Documents / Library", crumb: "Documents" },
  ];

  const here = (location.pathname.split("/").pop() || "").toLowerCase();
  let deepTrail = [];

  function currentPage() {
    for (let i = 0; i < pages.length; i++) {
      const p = pages[i];
      if (!p.href) continue;
      const file = p.href.split("/").pop().toLowerCase();
      if (here && file === here) return p;
    }
    return null;
  }

  function buildNav() {
    const nav = document.getElementById("nav");
    if (!nav) return null;
    nav.setAttribute("aria-label", "NR2 optical pages");
    const frag = document.createDocumentFragment();
    const brand = document.createElement("a");
    brand.className = "brand";
    brand.href = "/nr2-optical-beam-touch-mockup.html";
    brand.textContent = "NR2 · OPTICAL";
    brand.title = "Main landing";
    frag.appendChild(brand);

    pages.forEach(function (p) {
      if (p.group) {
        const g = document.createElement("div");
        g.className = "group";
        g.textContent = p.group;
        frag.appendChild(g);
        return;
      }
      const a = document.createElement("a");
      a.href = p.href;
      a.textContent = p.label;
      const file = (p.href.split("/").pop() || "").toLowerCase();
      if (here && file === here) {
        a.className = "on";
        a.setAttribute("aria-current", "page");
      }
      frag.appendChild(a);
    });

    nav.textContent = "";
    nav.appendChild(frag);
    return nav;
  }

  function ensureCrumb() {
    let crumb = document.getElementById("nr2-crumb");
    if (crumb) return crumb;
    const main = document.querySelector(".shell > .main, main.main");
    if (!main) return null;
    crumb = document.createElement("nav");
    crumb.id = "nr2-crumb";
    crumb.className = "nr2-crumb";
    crumb.setAttribute("aria-label", "Breadcrumb");
    main.insertBefore(crumb, main.firstChild);
    return crumb;
  }

  function renderCrumb() {
    const crumb = ensureCrumb();
    if (!crumb) return null;
    const cur = currentPage();
    const segments = [
      { label: "NR2", href: "/nr2-optical-beam-touch-mockup.html" },
      { label: "Optical", href: "/nr2-optical-pages-hub.html" },
    ];
    if (cur) {
      segments.push({
        label: cur.crumb || cur.label,
        href: deepTrail.length ? cur.href : null,
        current: !deepTrail.length,
      });
    } else if (here) {
      segments.push({ label: here.replace(/^nr2-optical-page-/, "").replace(/\.html$/, ""), current: true });
    }
    deepTrail.forEach(function (seg, idx) {
      const last = idx === deepTrail.length - 1;
      segments.push({
        label: String(seg.label || seg),
        href: last ? null : seg.href || null,
        current: last,
      });
    });

    crumb.textContent = "";
    const ol = document.createElement("ol");
    segments.forEach(function (seg, idx) {
      const li = document.createElement("li");
      if (seg.current || (!seg.href && idx === segments.length - 1)) {
        const span = document.createElement("span");
        span.className = "nr2-crumb-here";
        span.setAttribute("aria-current", "page");
        span.textContent = seg.label;
        li.appendChild(span);
      } else if (seg.href) {
        const a = document.createElement("a");
        a.href = seg.href;
        a.textContent = seg.label;
        li.appendChild(a);
      } else {
        const span = document.createElement("span");
        span.textContent = seg.label;
        li.appendChild(span);
      }
      ol.appendChild(li);
    });
    crumb.appendChild(ol);
    return crumb;
  }

  function setDeepTrail(segments) {
    deepTrail = Array.isArray(segments)
      ? segments
          .map(function (s) {
            if (s == null || s === "") return null;
            if (typeof s === "string") return { label: s };
            return { label: String(s.label || ""), href: s.href || null };
          })
          .filter(Boolean)
      : [];
    renderCrumb();
    return deepTrail;
  }

  function clearDeepTrail() {
    return setDeepTrail([]);
  }

  function focusPageHeading() {
    if (window.NR2OpticalWire && typeof window.NR2OpticalWire.focusMainHeading === "function") {
      window.NR2OpticalWire.focusMainHeading({ preventScroll: false });
      return;
    }
    const h1 = document.querySelector(".main h1, main h1, h1");
    if (!h1) return;
    if (!h1.hasAttribute("tabindex")) h1.setAttribute("tabindex", "-1");
    try {
      h1.focus({ preventScroll: true });
    } catch (_) {
      h1.focus();
    }
  }

  buildNav();
  renderCrumb();

  function bootMotionFromNav() {
    if (window.NR2OpticalWire && typeof window.NR2OpticalWire.bootMotionGrammar === "function") {
      window.NR2OpticalWire.bootMotionGrammar();
      return;
    }
    try {
      if (
        window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ) {
        document.documentElement.classList.add("nr2-reduced-motion");
        return;
      }
    } catch (_) {
      /* ignore */
    }
    if (document.documentElement.getAttribute("data-nr2-motion") === "off") return;
    document.documentElement.classList.add("nr2-motion");
    const main = document.querySelector(".shell > .main, main.main");
    if (main) main.classList.add("nr2-motion-enter");
  }
  // page-wire may load after nav — retry once for HAL / thin pages
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      bootMotionFromNav();
      setTimeout(bootMotionFromNav, 0);
      setTimeout(focusPageHeading, 30);
    });
  } else {
    bootMotionFromNav();
    setTimeout(bootMotionFromNav, 0);
    setTimeout(focusPageHeading, 30);
  }

  window.NR2OpticalNav = {
    pages: pages,
    currentPage: currentPage,
    setDeepTrail: setDeepTrail,
    clearDeepTrail: clearDeepTrail,
    renderCrumb: renderCrumb,
    focusPageHeading: focusPageHeading,
  };
})();
