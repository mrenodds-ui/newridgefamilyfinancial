import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { FinancialSummaryResponse } from "../api/client";
import { fetchFinancialSummary, fetchHalStatus } from "../api/client";
import ClaimsWorkbenchPage from "../pages/ClaimsWorkbenchPage";

vi.mock("../api/client", async () => {
  const actual = await vi.importActual<typeof import("../api/client")>("../api/client");
  return {
    ...actual,
    fetchFinancialSummary: vi.fn(),
    fetchHalStatus: vi.fn(),
    fetchHalPatientDossier: vi.fn(),
    generateHalInsuranceNarrative: vi.fn(),
  };
});

function buildHalStatus() {
  return {
    mode: "local",
    financial_sources: {
      softdent: {
        live_claims: {
          available: false,
          health: "missing",
          source_backend: "missing",
          confidence_label: "manual review",
          review_required: true,
          excerpt: "No approved export file is available yet.",
          source_file: "missing",
          review_flags: [],
        },
        live_clinical_notes: {
          available: false,
          health: "missing",
          source_backend: "missing",
          confidence_label: "manual review",
          review_required: true,
          excerpt: "No approved export file is available yet.",
          source_file: "missing",
          review_flags: [],
        },
        live_transaction_feed: {
          available: false,
          health: "missing",
          source_backend: "missing",
          confidence_label: "manual review",
          review_required: true,
          excerpt: "No approved export file is available yet.",
          source_file: "missing",
          review_flags: [],
        },
      },
    },
  } as unknown as Awaited<ReturnType<typeof fetchHalStatus>>;
}

function buildFinancialSummary(): FinancialSummaryResponse {
  return {
    generatedAt: "2026-06-22T10:00:00Z",
    latestSoftDentRefreshAt: "2026-06-22T09:45:00Z",
    dataFreshnessStatus: "fresh",
    sourceReview: null,
    softDentCoverage: null,
    softDentCoverageMetrics: null,
    claimsSummary: null,
    lastRefreshed: "2026-06-22T09:50:00Z",
    latestDailyKpi: null,
    latestAr: null,
    monthlyKpis: [],
    trailing12Months: [],
    calendarYearKpis: [],
    fourYearMonthlyKpis: [],
    providerProduction: [],
    topAdaCodes: [],
    quickBooksStatus: null,
    quickBooksExpenseCategories: [],
    quickBooksMonthlyExpenses: [],
    quickBooksProfitLossSummary: [],
    quickBooksEbitdaCandidates: [],
    dataFreshnessWarnings: [],
    currentMonthProduction: null,
    currentYearProduction: null,
    healthFlags: [],
  } as FinancialSummaryResponse;
}

function renderWithQuery(ui: React.ReactNode) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </MemoryRouter>,
  );
}

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("ClaimsWorkbenchPage", () => {
  it("renders safety badges and source status strip", async () => {
    vi.mocked(fetchHalStatus).mockResolvedValue(buildHalStatus());
    vi.mocked(fetchFinancialSummary).mockResolvedValue(buildFinancialSummary());

    renderWithQuery(<ClaimsWorkbenchPage />);

    expect(await screen.findByRole("heading", { name: "Patient Claims Workbench" })).toBeInTheDocument();
    expect(screen.getByText("Human Review Required")).toBeInTheDocument();
    expect(screen.getByText("Not Submitted")).toBeInTheDocument();
    expect(screen.getAllByText("Awaiting export").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("Not quantified yet")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Lookup patient dossier" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Generate narrative" })).toBeInTheDocument();
  });
});
