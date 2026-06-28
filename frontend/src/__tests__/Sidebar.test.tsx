import { cleanup, render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";

import Sidebar from "../layout/Sidebar";

function renderSidebar() {
  render(
    <MemoryRouter>
      <Sidebar />
    </MemoryRouter>,
  );
}

afterEach(() => {
  cleanup();
});

describe("Sidebar navigation", () => {
  it("puts staff workflows in an Office group", () => {
    renderSidebar();
    expect(screen.getByText("Office")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Command Center" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Claims" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ask HAL" })).toBeInTheDocument();
  });

  it("shows source-system and financial pages under Owner / Admin", () => {
    renderSidebar();
    const ownerLabel = screen.getByText("Owner / Admin");
    const ownerSection = ownerLabel.closest("section");
    expect(ownerSection).not.toBeNull();
    const owner = within(ownerSection as HTMLElement);
    expect(owner.getByRole("link", { name: "SoftDent" })).toBeInTheDocument();
    expect(owner.getByRole("link", { name: "QuickBooks" })).toBeInTheDocument();
    expect(owner.getByRole("link", { name: "Imports" })).toBeInTheDocument();
    expect(owner.getByRole("link", { name: "EBITDA" })).toBeInTheDocument();
    expect(owner.getByRole("link", { name: "Financial dashboard" })).toBeInTheDocument();
  });

  it("de-emphasizes the Owner / Admin section but not the Office section", () => {
    renderSidebar();
    const officeSection = screen.getByText("Office").closest("section");
    const ownerSection = screen.getByText("Owner / Admin").closest("section");
    expect(officeSection?.className).not.toContain("dashboard-sidebar__section--muted");
    expect(ownerSection?.className).toContain("dashboard-sidebar__section--muted");
  });
});
