import { useMemo, useState } from "react";
import { NavLink } from "react-router-dom";

import { useAuthSession } from "../hooks/useAuthSession";

type NavItem = {
  label: string;
  path: string;
  requiresAdmin?: boolean;
};

type NavGroup = {
  label: string;
  items: NavItem[];
};

const navGroups: NavGroup[] = [
  {
    label: "Overview",
    items: [
      { label: "Dashboard", path: "/" },
      { label: "Ask HAL", path: "/dashboard/hal" },
      { label: "HAL Home", path: "/hal-landing" },
      { label: "Trends", path: "/trends" },
      { label: "Settings", path: "/settings" },
    ],
  },
  {
    label: "Financials",
    items: [
      { label: "SoftDent", path: "/softdent" },
      { label: "QuickBooks", path: "/quickbooks" },
      { label: "Expenses", path: "/expenses" },
      { label: "A/R", path: "/ar" },
      { label: "EBITDA", path: "/ebitda" },
    ],
  },
  {
    label: "Operations",
    items: [
      { label: "Claims", path: "/claims-workbench" },
      { label: "Documents", path: "/accounting-documents" },
      { label: "Library", path: "/document-library" },
      { label: "Policy", path: "/accounting-policy" },
      { label: "Journal", path: "/journal-draft" },
      { label: "Posting", path: "/posting-queue" },
    ],
  },
  {
    label: "Administration",
    items: [{ label: "Admin", path: "/admin", requiresAdmin: true }],
  },
];

function canShowItem(item: NavItem, isAuthenticated: boolean, isRoleKnown: boolean, isLoading: boolean, isAdmin: boolean) {
  if (!item.requiresAdmin) {
    return true;
  }
  if (!isAuthenticated) {
    return true;
  }
  if (!isRoleKnown || isLoading) {
    return true;
  }
  return isAdmin;
}

export default function Sidebar() {
  const { authenticatedUsername, isAuthenticated, isAdmin, isLoading, isRoleKnown, isSessionAuthenticated } = useAuthSession();
  const [query, setQuery] = useState("");
  const normalizedQuery = query.trim().toLowerCase();
  const visibleNavGroups = useMemo(
    () =>
      navGroups
        .map((group) => ({
          ...group,
          items: group.items.filter((item) => {
            if (!canShowItem(item, isAuthenticated, isRoleKnown, isLoading, isAdmin)) {
              return false;
            }

            if (!normalizedQuery) {
              return true;
            }

            return item.label.toLowerCase().includes(normalizedQuery) || group.label.toLowerCase().includes(normalizedQuery);
          }),
        }))
        .filter((group) => group.items.length > 0),
    [isAdmin, isAuthenticated, isLoading, isRoleKnown, normalizedQuery],
  );
  const sessionTitle = isSessionAuthenticated ? authenticatedUsername ?? "Connected workspace" : "Guest workspace";
  const sessionDetail = isSessionAuthenticated
    ? "Backend session is active for live dashboard, documents, and HAL data."
    : "Sign in from the banner to unlock verified accounting and HAL data.";

  return (
    <aside className="dashboard-sidebar">
      <div className="dashboard-sidebar__brand">
        <div className="dashboard-sidebar__brand-mark" aria-hidden="true">
          NR
        </div>
        <div className="dashboard-sidebar__brand-copy">
          <span className="dashboard-sidebar__brand-kicker">Financial OS</span>
          <strong>New Ridge Family Financial</strong>
        </div>
      </div>
      <label className="dashboard-sidebar__search">
        <span className="dashboard-sidebar__search-label">Quick jump</span>
        <input
          className="dashboard-sidebar__search-input"
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search pages"
          aria-label="Search dashboard pages"
        />
      </label>
      <nav className="dashboard-sidebar__sections" aria-label="Primary navigation">
        {visibleNavGroups.map((group) => (
          <section key={group.label} className="dashboard-sidebar__section">
            <div className="dashboard-sidebar__section-label">{group.label}</div>
            <ul className="dashboard-sidebar__nav">
              {group.items.map((item) => (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      isActive ? "dashboard-sidebar__link dashboard-sidebar__link--active" : "dashboard-sidebar__link"
                    }
                    end={item.path === "/"}
                  >
                    {item.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </nav>
      <div className="dashboard-sidebar__footer">
        <span className="dashboard-sidebar__footer-label">Workspace</span>
        <strong>{sessionTitle}</strong>
        <span className="dashboard-sidebar__footer-copy">{sessionDetail}</span>
        <NavLink to="/settings" className="dashboard-sidebar__footer-link">
          Open settings
        </NavLink>
      </div>
    </aside>
  );
}
