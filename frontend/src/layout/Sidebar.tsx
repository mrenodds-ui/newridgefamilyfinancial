import { useMemo, useState } from "react";
import { NavLink } from "react-router-dom";
import { appBranding } from "../config/branding";

type NavItem = {
  label: string;
  path: string;
};

type NavGroup = {
  label: string;
  items: NavItem[];
  muted?: boolean;
};

const navGroups: NavGroup[] = [
  {
    label: "Office",
    items: [
      { label: "Command Center", path: "/dashboard/hal" },
      { label: "Claims", path: "/claims-workbench" },
      { label: "Narratives", path: "/insurance-narratives" },
      { label: "Documents", path: "/accounting-documents" },
      { label: "Library", path: "/document-library" },
      { label: "Ask HAL", path: "/dashboard/hal" },
    ],
  },
  {
    label: "Owner / Admin",
    muted: true,
    items: [
      { label: "Financial dashboard", path: "/" },
      { label: "SoftDent", path: "/softdent" },
      { label: "QuickBooks", path: "/quickbooks" },
      { label: "Imports", path: "/imports" },
      { label: "A/R details", path: "/ar" },
      { label: "EBITDA", path: "/ebitda" },
      { label: "Expenses", path: "/expenses" },
      { label: "Trends", path: "/trends" },
      { label: "Posting", path: "/posting-queue" },
      { label: "Journal", path: "/journal-draft" },
      { label: "Policy", path: "/accounting-policy" },
      { label: "Settings", path: "/settings" },
      { label: "Admin", path: "/admin" },
    ],
  },
];

export default function Sidebar() {
  const [query, setQuery] = useState("");
  const normalizedQuery = query.trim().toLowerCase();
  const visibleNavGroups = useMemo(
    () =>
      navGroups
        .map((group) => ({
          ...group,
          items: group.items.filter((item) => {
            if (!normalizedQuery) {
              return true;
            }

            return item.label.toLowerCase().includes(normalizedQuery) || group.label.toLowerCase().includes(normalizedQuery);
          }),
        }))
        .filter((group) => group.items.length > 0),
    [normalizedQuery],
  );

  return (
    <aside className="dashboard-sidebar">
      <div className="dashboard-sidebar__brand">
        <div className="dashboard-sidebar__brand-mark" aria-hidden="true">
          <svg className="dashboard-sidebar__tooth-mark" viewBox="0 0 64 64" focusable="false">
            <title>New Ridge tooth logo</title>
            <path
              d="M20.9 7.8c4.4 0 7.1 2.4 11.1 2.4s6.7-2.4 11.1-2.4c7.8 0 13.2 6.3 13.2 15.1 0 5.4-2.4 10.4-4.7 15.2-2.2 4.6-3.4 9.7-4.4 14.7-.6 3.1-2.5 5.2-5.1 5.2-3.1 0-4.5-2.9-5.6-6.4l-2.1-6.7c-.7-2.3-1.4-3.8-2.4-3.8s-1.7 1.5-2.4 3.8l-2.1 6.7c-1.1 3.5-2.5 6.4-5.6 6.4-2.6 0-4.5-2.1-5.1-5.2-1-5-2.2-10.1-4.4-14.7-2.3-4.8-4.7-9.8-4.7-15.2C7.7 14.1 13.1 7.8 20.9 7.8Z"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="4"
            />
          </svg>
        </div>
        <div className="dashboard-sidebar__brand-copy">
          <span className="dashboard-sidebar__brand-kicker">{appBranding.kicker}</span>
          <strong>{appBranding.name}</strong>
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
          <section
            key={group.label}
            className={group.muted ? "dashboard-sidebar__section dashboard-sidebar__section--muted" : "dashboard-sidebar__section"}
          >
            <div className="dashboard-sidebar__section-label">{group.label}</div>
            <ul className="dashboard-sidebar__nav">
              {group.items.map((item) => (
                <li key={`${group.label}-${item.label}-${item.path}`}>
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
        <strong>Mission control</strong>
        <span className="dashboard-sidebar__footer-copy">{appBranding.name} mockup pages.</span>
        <NavLink to="/settings" className="dashboard-sidebar__footer-link">
          Open settings
        </NavLink>
      </div>
    </aside>
  );
}
