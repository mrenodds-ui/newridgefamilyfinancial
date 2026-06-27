import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("../components/dashboard/ImportPanel", () => ({
  default: () => <div data-testid="import-panel">Import panel</div>,
}));

import ImportsPage from "../pages/ImportsPage";

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("ImportsPage", () => {
  it("renders the page-surface hero and import panel", () => {
    render(<ImportsPage />);

    expect(screen.getByRole("heading", { name: "Bring in files" })).toBeInTheDocument();
    expect(screen.getByText("Data sources / Imports")).toBeInTheDocument();
    expect(screen.getByText("Admin Upload Only")).toBeInTheDocument();
    expect(screen.getByText("No Writeback")).toBeInTheDocument();
    expect(screen.getByTestId("import-panel")).toBeInTheDocument();
  });
});
