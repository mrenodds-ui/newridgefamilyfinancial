import { useQuery } from "@tanstack/react-query";

import { formatCurrency } from "../../utils/formatting";
import { fetchFinancialSummary } from "../api/client";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { ARAgingBarChart } from "../components/dashboard/ARAgingBarChart";
import { ChartCard } from "../components/dashboard/ChartCard";
import { CurrencyLineChart } from "../components/dashboard/CurrencyLineChart";
import { buildProductionCollectionsSeries, selectLatestMonthlyKpi } from "../components/dashboard/financialDashboardSummary";
import { SummaryCard } from "../components/dashboard/SummaryCard";

function formatCurrencyValue(value: number | null | undefined) {
  return value === null || value === undefined ? "Unavailable" : formatCurrency(value);
}

export default function SoftDentPage() {
  const financialSummaryQuery = useQuery({
    queryKey: ["financial-summary"],
    queryFn: fetchFinancialSummary,
  });

  if (financialSummaryQuery.isPending) {
    return (
      <div className="dashboard-page">
        <LoadingSpinner label="Loading SoftDent financials..." />
      </div>
    );
  }

  if (financialSummaryQuery.isError || !financialSummaryQuery.data) {
    return (
      <div className="dashboard-page">
        <div className="page-state-card page-state-card--error">Unable to load live SoftDent financial data.</div>
      </div>
    );
  }

  const financialSummary = financialSummaryQuery.data;

  const latestAr = financialSummary.latestAr;
  const softDentCoverage = financialSummary.softDentCoverage ?? null;
  const softDentReview = financialSummary.sourceReview?.softDent ?? null;
  const monthlyKpi = selectLatestMonthlyKpi(financialSummary.monthlyKpis);
  const trailing12Months = buildProductionCollectionsSeries(financialSummary.trailing12Months);
  const collectionPercent = monthlyKpi?.collection_rate != null ? Math.round(monthlyKpi.collection_rate) : null;
  const arAging = latestAr
    ? [
        { name: "Current", value: latestAr.current_balance ?? 0 },
        { name: "31-60", value: latestAr.balance_30 ?? 0 },
        { name: "61-90", value: latestAr.balance_60 ?? 0 },
        { name: "90+", value: latestAr.balance_90 ?? 0 },
      ]
    : [];
  const olderArBalance = latestAr ? (latestAr.balance_60 ?? 0) + (latestAr.balance_90 ?? 0) : 0;

  return (
    <div className="dashboard-page">
      <header className="page-header">
        <p className="eyebrow">SoftDent</p>
        <h1>Practice Performance</h1>
        <div className="dashboard-description">Production, collections, and receivables from your practice-management workflow.</div>
      </header>
      <section className="dashboard-toolbar" aria-label="SoftDent summary">
        <div>
          <div className="dashboard-toolbar__label">Collections pace</div>
          <div className="dashboard-toolbar__value">{collectionPercent === null ? "Unavailable" : `${collectionPercent}%`}</div>
        </div>
        <div>
          <div className="dashboard-toolbar__label">Total A/R</div>
          <div className="dashboard-toolbar__value">{formatCurrencyValue(latestAr?.total_ar)}</div>
        </div>
        <div>
          <div className="dashboard-toolbar__label">90+ A/R</div>
          <div className="dashboard-toolbar__value">{formatCurrencyValue(latestAr?.balance_90)}</div>
        </div>
      </section>
      <div className="kpi-grid">
        <SummaryCard title="Production">
          <div>
            Current month gross: <strong>{formatCurrencyValue(monthlyKpi?.gross_production)}</strong>
          </div>
          <div>
            Current month net: <strong>{formatCurrencyValue(monthlyKpi?.net_production)}</strong>
          </div>
        </SummaryCard>
        <SummaryCard title="Collections">
          <div>
            Current month: <strong>{formatCurrencyValue(monthlyKpi?.collections)}</strong>
          </div>
          <div>
            Collection %: <strong>{collectionPercent === null ? "N/A" : `${collectionPercent}%`}</strong>
          </div>
        </SummaryCard>
        <SummaryCard title="A/R Aging">
          <div>
            Total: <strong>{formatCurrencyValue(latestAr?.total_ar)}</strong>
          </div>
          <div>
            90+: <strong>{formatCurrencyValue(latestAr?.balance_90)}</strong>
          </div>
        </SummaryCard>
        <SummaryCard title="Receivables Focus">
          <div>
            Current A/R: <strong>{formatCurrencyValue(latestAr?.current_balance)}</strong>
          </div>
          <div>
            60+ aging: <strong>{formatCurrencyValue(olderArBalance)}</strong>
          </div>
        </SummaryCard>
      </div>
      <div className="dashboard-charts">
        <ChartCard title="Production Trend">
          <CurrencyLineChart data={trailing12Months} lines={[{ dataKey: "production", name: "Production", color: "#D6B15E" }]} />
        </ChartCard>
        <ChartCard title="Collections Trend">
          <CurrencyLineChart data={trailing12Months} lines={[{ dataKey: "collections", name: "Collections", color: "#78A86B" }]} />
        </ChartCard>
        <ChartCard title="A/R Aging">
          <ARAgingBarChart data={arAging} />
        </ChartCard>
      </div>
      <section className="dashboard-card">
        <div className="dashboard-card__title">Collections Focus</div>
        <div className="dashboard-kpi-main">{formatCurrencyValue(monthlyKpi?.collections)}</div>
        <div className="dashboard-kpi-label">Current month collections</div>
        <div className="dashboard-kpi-support">
          <span>
            Gross production: <strong>{formatCurrencyValue(monthlyKpi?.gross_production)}</strong>
          </span>
          <span>
            Net production: <strong>{formatCurrencyValue(monthlyKpi?.net_production)}</strong>
          </span>
          <span>
            Older A/R: <strong>{formatCurrencyValue(olderArBalance)}</strong>
          </span>
        </div>
      </section>
    </div>
  );
}
