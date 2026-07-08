/** Moonshot page panel layouts — inlined manifest (no external JSON). */
const MOONSHOT_PAGE_LAYOUTS = {
  "version": 1,
  "source": "moonshot-kimi-k2.6-elite",
  "generated": "2026-07-08",
  "pages": {
    "financial": {
      "title": "Owner Financial Dashboard",
      "shell": "widget-grid",
      "panels": [
        {
          "id": "fin-alert-ticker",
          "type": "custom",
          "widgetKey": "nr2AlertTicker",
          "colSpan": 12,
          "title": "Exception Alert Ticker",
          "dataBind": "PageCanvasData.nr2AlertTicker()"
        },
        {
          "id": "fin-hero-kpis",
          "type": "hero-kpi",
          "colSpan": 12,
          "dataBind": "PageCanvasData.financialKpis()",
          "kpis": [
            { "widgetKey": "practiceFinancialOverview", "label": "Production MTD" },
            { "widgetKey": "financialProductionTrend", "label": "Collections MTD" },
            { "widgetKey": "payerMixAndCollections", "label": "Net Income YTD" },
            { "widgetKey": "nr2KpiRibbon", "label": "A/R Days" },
            { "widgetKey": "nr2GoalScorecard", "label": "Goal Attainment" }
          ]
        },
        {
          "id": "fin-monthly-trend",
          "type": "chart",
          "widgetKey": "nr2MonthlyTrendCombo",
          "colSpan": 8,
          "title": "Executive Monthly Trend",
          "dataBind": "PageCanvasData.nr2MonthlyTrendCombo()",
          "chartType": "dual"
        },
        {
          "id": "fin-collection-lag",
          "type": "gauge",
          "widgetKey": "nr2CollectionLag",
          "colSpan": 4,
          "title": "Collection Lag (DSO)",
          "dataBind": "PageCanvasData.nr2CollectionLag()"
        },
        {
          "id": "fin-reconciliation",
          "type": "table",
          "widgetKey": "nr2ProductionReconciliation",
          "colSpan": 6,
          "title": "Production vs QuickBooks Reconciliation",
          "dataBind": "PageCanvasData.nr2ProductionReconciliation()"
        },
        {
          "id": "fin-daily-production",
          "type": "chart",
          "widgetKey": "softdentProductionDaily",
          "colSpan": 6,
          "title": "SoftDent Production Trend",
          "dataBind": "PageCanvasData.softdentProductionDailySeries()",
          "chartType": "bar"
        },
        {
          "id": "fin-provider-performance",
          "type": "stat-grid",
          "widgetKey": "providerPerformance",
          "colSpan": 6,
          "title": "Provider Performance",
          "dataBind": "PageCanvasData.providerBars()"
        },
        {
          "id": "fin-provider-production",
          "type": "table",
          "widgetKey": "softdentProviderProduction",
          "colSpan": 6,
          "title": "Provider Production (Daily)",
          "dataBind": "PageCanvasData.softdentProviderProductionData()"
        },
        {
          "id": "fin-provider-comp",
          "type": "stat-grid",
          "widgetKey": "nr2ProviderCompensationWidget",
          "colSpan": 6,
          "title": "Provider Production Share",
          "dataBind": "PageCanvasData.nr2ProviderCompensation()"
        },
        {
          "id": "fin-collections-daily",
          "type": "chart",
          "widgetKey": "softdentCollectionsDaily",
          "colSpan": 6,
          "title": "Collections Trend",
          "dataBind": "PageCanvasData.softdentCollectionsDailySeries()",
          "chartType": "bar"
        },
        {
          "id": "fin-new-patients-mtd",
          "type": "stat-grid",
          "widgetKey": "softdentNewPatientsMTD",
          "colSpan": 4,
          "title": "New Patients (MTD)",
          "dataBind": "PageCanvasData.softdentNewPatientsMtdData()"
        },
        {
          "id": "fin-claims-outstanding",
          "type": "stat-grid",
          "widgetKey": "softdentClaimsOutstanding",
          "colSpan": 4,
          "title": "Outstanding Claims",
          "dataBind": "PageCanvasData.softdentClaimsOutstandingData()"
        },
        {
          "id": "fin-new-patients",
          "type": "chart",
          "widgetKey": "newPatients",
          "colSpan": 4,
          "title": "New Patient Flow",
          "dataBind": "PageCanvasData.metrics('newPatients')",
          "chartType": "bar"
        },
        {
          "id": "fin-appointments",
          "type": "table",
          "widgetKey": "softdentAppointmentsSnapshot",
          "colSpan": 12,
          "title": "Appointments Snapshot",
          "dataBind": "PageCanvasData.softdentAppointmentsSnapshotData()"
        }
      ]
    },
    "taxes": {
      "title": "S Corp Tax Planning",
      "shell": "widget-grid",
      "panels": [
        {
          "id": "tax-qb-pl",
          "type": "table",
          "widgetKey": "quickbooksProfitLossDetail",
          "colSpan": 6,
          "title": "Book Income (QuickBooks YTD)",
          "dataBind": "PageCanvasData.quickbooksPlRows()"
        },
        {
          "id": "tax-ebitda",
          "type": "table",
          "widgetKey": "ebitdaNormalization",
          "colSpan": 6,
          "title": "Owner Add-backs & Adjustments",
          "dataBind": "PageCanvasData.ebitdaRows()"
        },
        {
          "id": "tax-monthly-revenue",
          "type": "chart",
          "widgetKey": "quickbooksMonthlyRevenue",
          "colSpan": 6,
          "title": "Monthly Revenue Trend",
          "dataBind": "PageCanvasData.quickbooksMonthlyRevenueSeries()",
          "chartType": "bar"
        },
        {
          "id": "tax-net-income",
          "type": "stat-grid",
          "widgetKey": "quickbooksNetIncomeSummary",
          "colSpan": 6,
          "title": "Net Income Summary",
          "dataBind": "PageCanvasData.quickbooksNetIncomeSummary()"
        },
        {
          "id": "tax-balance-sheet",
          "type": "table",
          "widgetKey": "quickbooksBalanceSheetSummary",
          "colSpan": 6,
          "title": "Balance Sheet Summary",
          "dataBind": "PageCanvasData.quickbooksBalanceSheetSummary()"
        },
        {
          "id": "tax-cash-flow",
          "type": "chart",
          "widgetKey": "quickbooksCashFlowTrend",
          "colSpan": 6,
          "title": "Cash Flow Trend",
          "dataBind": "PageCanvasData.quickbooksCashFlowTrend()",
          "chartType": "dual"
        },
        {
          "id": "tax-revenue-service",
          "type": "donut",
          "widgetKey": "quickbooksRevenueByService",
          "colSpan": 4,
          "title": "Revenue by Service",
          "dataBind": "PageCanvasData.quickbooksRevenueByService()",
          "chartType": "donut"
        },
        {
          "id": "tax-ar-aging",
          "type": "table",
          "widgetKey": "quickbooksArAging",
          "colSpan": 8,
          "title": "QuickBooks A/R Aging",
          "dataBind": "PageCanvasData.quickbooksQbArAging()"
        },
        {
          "id": "tax-expense-breakdown",
          "type": "stat-grid",
          "widgetKey": "quickbooksExpenseBreakdown",
          "colSpan": 6,
          "title": "Operating Expenses",
          "dataBind": "PageCanvasData.quickbooksExpenseBars()"
        },
        {
          "id": "tax-ap",
          "type": "table",
          "widgetKey": "accountsPayableAutomation",
          "colSpan": 6,
          "title": "Accounts Payable",
          "dataBind": "PageCanvasData.metrics('accountsPayableAutomation')"
        },
        {
          "id": "tax-period-close",
          "type": "stat-grid",
          "widgetKey": "periodCloseAndPosting",
          "colSpan": 6,
          "title": "June Period Close",
          "dataBind": "PageCanvasData.documentsPeriodStats()"
        },
        {
          "id": "tax-journal-queue",
          "type": "table",
          "widgetKey": "journalPostingQueue",
          "colSpan": 6,
          "title": "June Journal Entries",
          "dataBind": "PageCanvasData.journalQueueItems()"
        }
      ]
    },
    "hal": {
      "title": "HAL Command Center",
      "shell": "dashboard-grid",
      "panels": [
        {
          "id": "hal-ask",
          "type": "custom",
          "widgetKey": "halAskHal",
          "colSpan": 12,
          "title": "Ask HAL",
          "dataBind": "PageCanvasData.widget('halAskHal')"
        },
        {
          "id": "hal-import-health",
          "type": "stat-grid",
          "widgetKey": "halImportHealth",
          "colSpan": 3,
          "title": "Import & Source Health",
          "dataBind": "PageCanvasData.integrationMetric('halImportHealth')"
        },
        {
          "id": "hal-fin-overview",
          "type": "stat-grid",
          "widgetKey": "practiceFinancialOverview",
          "colSpan": 3,
          "title": "Practice Financial Overview",
          "dataBind": "PageCanvasData.metrics('practiceFinancialOverview')"
        },
        {
          "id": "hal-care-delivery",
          "type": "stat-grid",
          "widgetKey": "careDeliveryPerformance",
          "colSpan": 3,
          "title": "Care Delivery Summary",
          "dataBind": "PageCanvasData.metrics('careDeliveryPerformance')"
        },
        {
          "id": "hal-qb-pl",
          "type": "stat-grid",
          "widgetKey": "quickbooksProfitLossDetail",
          "colSpan": 3,
          "title": "Profit & Loss Summary",
          "dataBind": "PageCanvasData.metrics('quickbooksProfitLossDetail')"
        },
        {
          "id": "hal-surfaces",
          "type": "kanban",
          "widgetKey": "officeManagerSurfaces",
          "colSpan": 12,
          "title": "Staff Work Surfaces",
          "dataBind": "PageCanvasData.metrics('officeManagerSurfaces')"
        }
      ]
    },
    "softdent": {
      "title": "Clinical & Practice Performance",
      "shell": "widget-grid",
      "panels": [
        {
          "id": "sd-kpi-care",
          "type": "hero-kpi",
          "widgetKey": "careDeliveryPerformance",
          "colSpan": 3,
          "title": "Care Delivery Summary",
          "dataBind": "PageCanvasData.softdentKpis()[0]"
        },
        {
          "id": "sd-kpi-np",
          "type": "hero-kpi",
          "widgetKey": "softdentNewPatientsMTD",
          "colSpan": 3,
          "title": "New Patients (MTD)",
          "dataBind": "PageCanvasData.softdentNewPatientsMtdData()"
        },
        {
          "id": "sd-kpi-ca",
          "type": "hero-kpi",
          "widgetKey": "caseAcceptance",
          "colSpan": 3,
          "title": "Case Acceptance Rate",
          "dataBind": "PageCanvasData.softdentKpis()[3]"
        },
        {
          "id": "sd-kpi-claims",
          "type": "hero-kpi",
          "widgetKey": "softdentClaimsOutstanding",
          "colSpan": 3,
          "title": "Open Claims",
          "dataBind": "PageCanvasData.claimsOutstandingKpi()"
        },
        {
          "id": "sd-chart-collections",
          "type": "chart",
          "widgetKey": "softdentCollectionsDaily",
          "chartType": "dual",
          "colSpan": 8,
          "title": "Collections Trend",
          "dataBind": "PageCanvasData.collectionsTrendSeries()"
        },
        {
          "id": "sd-chart-providers",
          "type": "chart",
          "widgetKey": "softdentProviderProduction",
          "chartType": "bar",
          "colSpan": 4,
          "title": "Provider Production",
          "dataBind": "PageCanvasData.providerPerformance()"
        },
        {
          "id": "sd-chart-ar",
          "type": "chart",
          "widgetKey": "softdentArAging",
          "chartType": "bar",
          "colSpan": 6,
          "title": "A/R Aging",
          "dataBind": "PageCanvasData.arAgingSeries()"
        },
        {
          "id": "sd-chart-responsibility",
          "type": "chart",
          "widgetKey": "softdentResponsibility",
          "chartType": "donut",
          "colSpan": 6,
          "title": "Insurance vs Patient Balance",
          "dataBind": "PageCanvasData.payerResponsibilitySplit()"
        },
        {
          "id": "sd-funnel-ca",
          "type": "funnel",
          "halSubpanel": "caseAcceptanceFunnel",
          "colSpan": 6,
          "title": "Case Acceptance Rate",
          "dataBind": "PageCanvasData.metrics('caseAcceptance')"
        },
        {
          "id": "sd-table-tx",
          "type": "table",
          "widgetKey": "treatmentPlanSummary",
          "colSpan": 6,
          "title": "Treatment Plans Presented",
          "dataBind": "PageCanvasData.treatmentPlanSummary()"
        },
        {
          "id": "sd-table-appts",
          "type": "table",
          "widgetKey": "softdentAppointmentsSnapshot",
          "colSpan": 6,
          "title": "Appointments Snapshot",
          "dataBind": "PageCanvasData.appointmentsSnapshot()"
        },
        {
          "id": "sd-stats-hygiene",
          "type": "stat-grid",
          "widgetKey": "hygieneRecall",
          "colSpan": 12,
          "title": "Hygiene & Recall",
          "dataBind": "PageCanvasData.hygieneRecall()"
        },
        {
          "id": "sd-grid-operatory",
          "type": "table",
          "widgetKey": "softdentOperatoryGrid",
          "colSpan": 12,
          "title": "Operatory Schedule",
          "dataBind": "PageCanvasData.operatorySchedule()"
        }
      ]
    },
    "narratives": {
      "title": "Insurance Narratives",
      "shell": "widget-grid",
      "panels": [
        {
          "id": "nar-composer",
          "type": "custom",
          "widgetKey": "narrativeWorkflow",
          "colSpan": 8,
          "title": "Narrative Composer",
          "dataBind": "PageCanvasData.narrativeWorkflow()"
        },
        {
          "id": "nar-templates",
          "type": "custom",
          "halSubpanel": "narrativeTemplates",
          "colSpan": 4,
          "title": "Procedure Templates",
          "dataBind": "PageCanvasData.narrativeTemplates()"
        },
        {
          "id": "nar-history",
          "type": "table",
          "halSubpanel": "narrativeHistory",
          "colSpan": 4,
          "title": "Draft History",
          "dataBind": "PageCanvasData.narrativeHistory()"
        }
      ]
    },
    "claims": {
      "title": "Claims Workbench",
      "shell": "widget-grid",
      "panels": [
        {
          "id": "clm-kpi-1",
          "type": "hero-kpi",
          "halSubpanel": "claimsKpiTotal",
          "colSpan": 4,
          "title": "Open Claims",
          "dataBind": "PageCanvasData.claimsKpis()[0]"
        },
        {
          "id": "clm-kpi-2",
          "type": "hero-kpi",
          "halSubpanel": "claimsKpiValue",
          "colSpan": 4,
          "title": "Outstanding Value",
          "dataBind": "PageCanvasData.claimsKpis()[1]"
        },
        {
          "id": "clm-kpi-3",
          "type": "hero-kpi",
          "halSubpanel": "claimsKpiDenied",
          "colSpan": 4,
          "title": "Denial Rate",
          "dataBind": "PageCanvasData.claimsKpis()[2]"
        },
        {
          "id": "clm-kanban",
          "type": "kanban",
          "widgetKey": "claimsPipeline",
          "colSpan": 8,
          "title": "Open Insurance Claims",
          "dataBind": "PageCanvasData.claimsPipeline()"
        },
        {
          "id": "clm-vol",
          "type": "chart",
          "halSubpanel": "claimsVolumeTrend",
          "chartType": "bar",
          "colSpan": 4,
          "title": "Submission Volume",
          "dataBind": "PageCanvasData.claimsVolumeTrend()"
        },
        {
          "id": "clm-payers",
          "type": "chart",
          "halSubpanel": "claimsPayerBreakdown",
          "chartType": "donut",
          "colSpan": 4,
          "title": "Payer Mix",
          "dataBind": "PageCanvasData.claimsPayerBreakdown()"
        },
        {
          "id": "clm-sidebar",
          "type": "custom",
          "halSubpanel": "claimsSidebar",
          "colSpan": 4,
          "title": "Claim detail sidebar",
          "dataBind": "PageCanvasData.firstClaim()"
        }
      ]
    },
    "ar": {
      "title": "A/R & Collections",
      "shell": "widget-grid",
      "panels": [
        {
          "id": "ar-hero-kpis",
          "type": "hero-kpi",
          "colSpan": 12,
          "title": "Revenue Cycle KPIs",
          "dataBind": "PageCanvasData.arKpis()"
        },
        {
          "id": "ar-aging-heatmap",
          "type": "heatmap",
          "widgetKey": "arAgingAndCollections",
          "colSpan": 8,
          "title": "Aging & Collections Trend",
          "dataBind": "PageCanvasData.arAgingHeatmap()"
        },
        {
          "id": "ar-distribution-donut",
          "type": "donut",
          "halSubpanel": "arDistribution",
          "colSpan": 4,
          "title": "A/R Distribution",
          "dataBind": "PageCanvasData.arDistribution()",
          "chartType": "donut"
        },
        {
          "id": "ar-followup-kanban",
          "type": "kanban",
          "widgetKey": "smartClaimsAndReceivables",
          "colSpan": 12,
          "title": "Follow-up Queue",
          "dataBind": "PageCanvasData.followUpQueue()"
        },
        {
          "id": "ar-outstanding-table",
          "type": "table",
          "widgetKey": "arOutstandingClaims",
          "colSpan": 12,
          "title": "Outstanding Claims",
          "dataBind": "PageCanvasData.outstandingClaims()"
        }
      ]
    },
    "quickbooks": {
      "title": "QuickBooks Integration",
      "shell": "dashboard-grid",
      "panels": [
        {
          "id": "qb-hero-kpis",
          "type": "hero-kpi",
          "colSpan": 12,
          "title": "Financial Performance",
          "dataBind": "PageCanvasData.quickbooksKpis()"
        },
        {
          "id": "qb-revenue-trend",
          "type": "chart",
          "widgetKey": "quickbooksMonthlyRevenue",
          "colSpan": 8,
          "title": "Profit & Loss Trend",
          "dataBind": "PageCanvasData.revenueTrendSeries()",
          "chartType": "dual"
        },
        {
          "id": "qb-revenue-service",
          "type": "donut",
          "widgetKey": "quickbooksRevenueByService",
          "colSpan": 4,
          "title": "Revenue by Service",
          "dataBind": "PageCanvasData.revenueByService()",
          "chartType": "donut"
        },
        {
          "id": "qb-pl-summary",
          "type": "stat-grid",
          "widgetKey": "quickbooksProfitLossDetail",
          "colSpan": 6,
          "title": "Profit & Loss Summary",
          "dataBind": "PageCanvasData.plSummary()"
        },
        {
          "id": "qb-net-income-gauge",
          "type": "gauge",
          "widgetKey": "quickbooksNetIncomeSummary",
          "colSpan": 6,
          "title": "Net Income Performance",
          "dataBind": "PageCanvasData.netIncomeGauge()"
        },
        {
          "id": "qb-balance-sheet",
          "type": "stat-grid",
          "widgetKey": "quickbooksBalanceSheetSummary",
          "colSpan": 6,
          "title": "Balance Sheet Summary",
          "dataBind": "PageCanvasData.balanceSheetMetrics()"
        },
        {
          "id": "qb-cash-flow",
          "type": "chart",
          "widgetKey": "quickbooksCashFlowTrend",
          "colSpan": 6,
          "title": "Cash Flow Trend",
          "dataBind": "PageCanvasData.cashFlowSeries()",
          "chartType": "line"
        },
        {
          "id": "qb-ebitda-funnel",
          "type": "funnel",
          "widgetKey": "ebitdaNormalization",
          "colSpan": 6,
          "title": "EBITDA Normalization",
          "dataBind": "PageCanvasData.ebitdaBridge()"
        },
        {
          "id": "qb-expense-breakdown",
          "type": "chart",
          "widgetKey": "quickbooksExpenseBreakdown",
          "colSpan": 6,
          "title": "Operating Expenses",
          "dataBind": "PageCanvasData.expenseBreakdown()",
          "chartType": "bar"
        },
        {
          "id": "qb-ar-aging",
          "type": "table",
          "widgetKey": "quickbooksArAging",
          "colSpan": 12,
          "title": "QuickBooks A/R Aging",
          "dataBind": "PageCanvasData.qbArAging()"
        }
      ]
    },
    "documents": {
      "title": "Accounting Documents",
      "shell": "widget-grid",
      "panels": [
        {
          "id": "doc-intake",
          "type": "table",
          "widgetKey": "documentIntakeQueue",
          "colSpan": 8,
          "title": "Recent Accounting Documents",
          "dataBind": "PageCanvasData.metrics('documentIntakeQueue')"
        },
        {
          "id": "doc-preview",
          "type": "custom",
          "widgetKey": "documentPreview",
          "colSpan": 4,
          "title": "Document Preview",
          "dataBind": "PageCanvasData.metrics('documentPreview')"
        },
        {
          "id": "period-close",
          "type": "gauge",
          "widgetKey": "periodCloseAndPosting",
          "colSpan": 6,
          "title": "June Period Close",
          "dataBind": "PageCanvasData.metrics('periodCloseAndPosting')"
        },
        {
          "id": "ap-auto",
          "type": "funnel",
          "widgetKey": "accountsPayableAutomation",
          "colSpan": 6,
          "title": "Accounts Payable",
          "dataBind": "PageCanvasData.metrics('accountsPayableAutomation')"
        },
        {
          "id": "journal-queue",
          "type": "table",
          "widgetKey": "journalPostingQueue",
          "colSpan": 12,
          "title": "Journal Entries",
          "dataBind": "PageCanvasData.metrics('journalPostingQueue')"
        },
        {
          "id": "doc-sources",
          "type": "stat-grid",
          "halSubpanel": "documentsSourceBreakdown",
          "colSpan": 12,
          "title": "Source breakdown",
          "dataBind": "PageCanvasData.documentsSourceBreakdown()"
        }
      ]
    },
    "library": {
      "title": "Document Library",
      "shell": "widget-grid",
      "panels": [
        {
          "id": "lib-facets",
          "type": "custom",
          "halSubpanel": "categoryFacets",
          "colSpan": 3,
          "title": "Categories",
          "dataBind": "PageCanvasData.libraryFacets()"
        },
        {
          "id": "lib-main",
          "type": "table",
          "widgetKey": "documentLibrary",
          "colSpan": 9,
          "title": "Library & Preview",
          "dataBind": "PageCanvasData.metrics('documentLibrary')"
        }
      ]
    },
    "office-manager": {
      "title": "Office Command Center",
      "shell": "dashboard-grid",
      "panels": [
        {
          "id": "om-priorities",
          "type": "kanban",
          "widgetKey": "officeManagerPriorities",
          "colSpan": 8,
          "title": "Today's Focus",
          "dataBind": "PageCanvasData.metrics('officeManagerPriorities')"
        },
        {
          "id": "om-tasks",
          "type": "table",
          "halSubpanel": "officeTaskQueue",
          "colSpan": 12,
          "title": "Office task queue",
          "dataBind": "PageCanvasData.officeTaskRows()"
        },
        {
          "id": "om-surfaces",
          "type": "stat-grid",
          "widgetKey": "officeManagerSurfaces",
          "colSpan": 4,
          "title": "Staff Work Surfaces",
          "dataBind": "PageCanvasData.metrics('officeManagerSurfaces')"
        }
      ]
    }
  }
};

if (typeof module !== "undefined" && module.exports) {
  module.exports = MOONSHOT_PAGE_LAYOUTS;
}
if (typeof globalThis !== "undefined") {
  globalThis.MOONSHOT_PAGE_LAYOUTS = MOONSHOT_PAGE_LAYOUTS;
}
if (typeof window !== "undefined") {
  window.MOONSHOT_PAGE_LAYOUTS = MOONSHOT_PAGE_LAYOUTS;
}
