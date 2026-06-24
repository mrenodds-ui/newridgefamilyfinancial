import { useQuery } from "@tanstack/react-query";

import { fetchFinancialSummary } from "../api/client";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ARAgingBarChart } from "../components/dashboard/ARAgingBarChart";
import { ChartCard } from "../components/dashboard/ChartCard";
import { CurrencyLineChart } from "../components/dashboard/CurrencyLineChart";
import { buildProductionCollectionsSeries, selectLatestMonthlyKpi } from "../components/dashboard/financialDashboardSummary";
import { SummaryCard } from "../components/dashboard/SummaryCard";

function formatCurrency(value: number) {
  return value.toLocaleString();
}

export default function ARCollectionsPage() {
  const financialSummaryQuery = useQuery({
    queryKey: ["financial-summary"],
    queryFn: fetchFinancialSummary,
  });

  if (financialSummaryQuery.isPending) {
    return (
      <div className="dashboard-page">
        <LoadingSpinner label="Loading A/R and collections..." />
      </div>
    );
  }

  if (financialSummaryQuery.isError || !financialSummaryQuery.data) {
    return (
      <div className="dashboard-page">
        <div className="page-state-card page-state-card--error">Unable to load live A/R data.</div>
      </div>
    );
  }

  const financialSummary = financialSummaryQuery.data;
  const latestAr = financialSummary.latestAr;
  const trailing12Months = buildProductionCollectionsSeries(financialSummary.trailing12Months);
  const arAging = latestAr
    ? [
        { name: "Current", value: latestAr.current_balance ?? 0 },
        { name: "31-60", value: latestAr.balance_30 ?? 0 },
        { name: "61-90", value: latestAr.balance_60 ?? 0 },
        { name: "90+", value: latestAr.balance_90 ?? 0 },
      ]
    : [];
  const olderArTotal = latestAr ? (latestAr.balance_60 ?? 0) + (latestAr.balance_90 ?? 0) : 0;
  const collectionPercent = selectLatestMonthlyKpi(financialSummary.monthlyKpis)?.collection_rate ?? null;

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <p className="eyebrow">Collections</p>
        <h1>A/R & Collections</h1>
        <div className="dashboard-description">Cash collection health and A/R aging.</div>
      </header>
      <section className="dashboard-toolbar" aria-label="Collections summary">
        <div>
          <div className="dashboard-toolbar__label">Total A/R</div>
          <div className="dashboard-toolbar__value">${latestAr ? formatCurrency(latestAr.total_ar ?? 0) : "0"}</div>
        </div>
        <div>
          <div className="dashboard-toolbar__label">60+ A/R</div>
          <div className="dashboard-toolbar__value">${formatCurrency(olderArTotal)}</div>
        </div>
        <div>
          <div className="dashboard-toolbar__label">Collection pace</div>
          <div className="dashboard-toolbar__value">{collectionPercent !== null ? `${Math.round(collectionPercent)}%` : "N/A"}</div>
        </div>
      </section>
      <div className="kpi-grid">
        <SummaryCard title="Total A/R">
          <div>
            <strong>${latestAr ? formatCurrency(latestAr.total_ar ?? 0) : "0"}</strong>
          </div>
        </SummaryCard>
        <SummaryCard title="90+ A/R">
          <div>
            <strong>${latestAr ? formatCurrency(latestAr.balance_90 ?? 0) : "0"}</strong>
          </div>
        </SummaryCard>
        <SummaryCard title="Collection %">
          <div>
            <strong>{collectionPercent !== null ? `${Math.round(collectionPercent)}%` : "N/A"}</strong>
          </div>
        </SummaryCard>
        <SummaryCard title="60+ A/R">
          <div>
            <strong>${formatCurrency(olderArTotal)}</strong>
          </div>
        </SummaryCard>
      </div>
      <div className="dashboard-charts">
        <ChartCard title="A/R Aging">
          <ARAgingBarChart data={arAging} />
        </ChartCard>
        <ChartCard title="Collections Trend">
          <CurrencyLineChart data={trailing12Months} lines={[{ dataKey: "collections", name: "Collections", color: "#78A86B" }]} />
        </ChartCard>
      </div>
      <section className="dashboard-card">
        <div className="dashboard-card__title">Collections Focus</div>
        <div className="dashboard-kpi-main">${latestAr ? formatCurrency(latestAr.balance_90 ?? 0) : "0"}</div>
        <div className="dashboard-kpi-label">A/R older than 90 days</div>
        <div className="dashboard-kpi-support">
          <span>
            Total A/R: <strong>${latestAr ? formatCurrency(latestAr.total_ar ?? 0) : "0"}</strong>
          </span>
          <span>
            60+ aging: <strong>${formatCurrency(olderArTotal)}</strong>
          </span>
          <span>
            Collection pace: <strong>{collectionPercent !== null ? `${Math.round(collectionPercent)}%` : "N/A"}</strong>
          </span>
        </div>
      </section>
    </div>
  );
}
