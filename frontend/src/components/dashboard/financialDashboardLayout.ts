import type { LayoutItem, ResponsiveLayouts } from "react-grid-layout/legacy";

export type FinancialDashboardBreakpoint = "lg" | "md" | "sm" | "xs" | "xxs";

export const FINANCIAL_DASHBOARD_LAYOUT_STORAGE_KEY = "financial-dashboard-layout-v1";

export const FINANCIAL_DASHBOARD_BREAKPOINTS: Record<FinancialDashboardBreakpoint, number> = {
  lg: 1200,
  md: 996,
  sm: 768,
  xs: 480,
  xxs: 0,
};

export const FINANCIAL_DASHBOARD_COLS: Record<FinancialDashboardBreakpoint, number> = {
  lg: 12,
  md: 10,
  sm: 6,
  xs: 4,
  xxs: 2,
};

export const FINANCIAL_DASHBOARD_TILE_IDS = [
  "case-acceptance",
  "ap-automation",
  "smart-claims",
  "revenue-analytics",
  "ai-follow-up",
  "featured",
  "payment-mix",
  "cashflow",
  "production-trend",
  "collections-trend",
  "expense-category",
  "monthly-expense-trend",
  "net-income-trend",
  "ar-aging",
  "trailing-collections",
] as const;

export type FinancialDashboardTileId = (typeof FINANCIAL_DASHBOARD_TILE_IDS)[number];
export type FinancialDashboardLayouts = ResponsiveLayouts<FinancialDashboardBreakpoint>;

const DASHBOARD_TILE_HEIGHTS: Record<FinancialDashboardTileId, number> = {
  "case-acceptance": 5,
  "ap-automation": 5,
  "smart-claims": 5,
  "revenue-analytics": 5,
  "ai-follow-up": 5,
  featured: 5,
  "payment-mix": 5,
  cashflow: 4,
  "production-trend": 4,
  "collections-trend": 4,
  "expense-category": 4,
  "monthly-expense-trend": 4,
  "net-income-trend": 4,
  "ar-aging": 4,
  "trailing-collections": 4,
};

const BREAKPOINT_SEQUENCE: readonly FinancialDashboardBreakpoint[] = ["lg", "md", "sm", "xs", "xxs"];

function createLayoutItem(id: FinancialDashboardTileId, x: number, y: number, w: number, h: number): LayoutItem {
  return { i: id, x, y, w, h, minW: Math.min(w, 2), minH: Math.min(h, 3) };
}

function buildSingleColumnLayout(cols: number): LayoutItem[] {
  let currentY = 0;

  return FINANCIAL_DASHBOARD_TILE_IDS.map((id) => {
    const item = createLayoutItem(id, 0, currentY, cols, DASHBOARD_TILE_HEIGHTS[id]);
    currentY += item.h;
    return item;
  });
}

function cloneLayouts(layouts: FinancialDashboardLayouts): FinancialDashboardLayouts {
  const next: FinancialDashboardLayouts = {};

  for (const breakpoint of BREAKPOINT_SEQUENCE) {
    next[breakpoint] = (layouts[breakpoint] ?? []).map((item) => ({ ...item }));
  }

  return next;
}

export const defaultFinancialDashboardLayouts: FinancialDashboardLayouts = {
  lg: [
    createLayoutItem("case-acceptance", 0, 0, 4, 5),
    createLayoutItem("ap-automation", 4, 0, 4, 5),
    createLayoutItem("smart-claims", 8, 0, 4, 5),
    createLayoutItem("revenue-analytics", 0, 5, 6, 5),
    createLayoutItem("ai-follow-up", 6, 5, 6, 5),
    createLayoutItem("featured", 0, 10, 8, 5),
    createLayoutItem("payment-mix", 8, 10, 4, 5),
    createLayoutItem("cashflow", 0, 15, 6, 4),
    createLayoutItem("production-trend", 6, 15, 3, 4),
    createLayoutItem("collections-trend", 9, 15, 3, 4),
    createLayoutItem("expense-category", 0, 19, 4, 4),
    createLayoutItem("monthly-expense-trend", 4, 19, 4, 4),
    createLayoutItem("net-income-trend", 8, 19, 4, 4),
    createLayoutItem("ar-aging", 0, 23, 6, 4),
    createLayoutItem("trailing-collections", 6, 23, 6, 4),
  ],
  md: [
    createLayoutItem("case-acceptance", 0, 0, 5, 5),
    createLayoutItem("ap-automation", 5, 0, 5, 5),
    createLayoutItem("smart-claims", 0, 5, 5, 5),
    createLayoutItem("revenue-analytics", 5, 5, 5, 5),
    createLayoutItem("ai-follow-up", 0, 10, 10, 5),
    createLayoutItem("featured", 0, 15, 10, 5),
    createLayoutItem("payment-mix", 0, 20, 5, 5),
    createLayoutItem("cashflow", 5, 20, 5, 4),
    createLayoutItem("production-trend", 0, 24, 5, 4),
    createLayoutItem("collections-trend", 5, 24, 5, 4),
    createLayoutItem("expense-category", 0, 28, 5, 4),
    createLayoutItem("monthly-expense-trend", 5, 28, 5, 4),
    createLayoutItem("net-income-trend", 0, 32, 5, 4),
    createLayoutItem("ar-aging", 5, 32, 5, 4),
    createLayoutItem("trailing-collections", 0, 36, 10, 4),
  ],
  sm: buildSingleColumnLayout(FINANCIAL_DASHBOARD_COLS.sm),
  xs: buildSingleColumnLayout(FINANCIAL_DASHBOARD_COLS.xs),
  xxs: buildSingleColumnLayout(FINANCIAL_DASHBOARD_COLS.xxs),
};

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function normalizeLayoutItem(item: Partial<LayoutItem> | null | undefined, fallback: LayoutItem): LayoutItem {
  if (!item) {
    return { ...fallback };
  }

  return {
    ...fallback,
    x: isFiniteNumber(item.x) ? item.x : fallback.x,
    y: isFiniteNumber(item.y) ? item.y : fallback.y,
    w: isFiniteNumber(item.w) ? item.w : fallback.w,
    h: isFiniteNumber(item.h) ? item.h : fallback.h,
  };
}

export function mergeFinancialDashboardLayouts(candidate: FinancialDashboardLayouts | null | undefined): FinancialDashboardLayouts {
  const next: FinancialDashboardLayouts = {};

  for (const breakpoint of BREAKPOINT_SEQUENCE) {
    const defaultLayout = defaultFinancialDashboardLayouts[breakpoint] ?? [];
    const savedLayout = candidate?.[breakpoint] ?? [];
    const savedById = new Map(savedLayout.map((item) => [item.i, item]));

    next[breakpoint] = defaultLayout.map((fallback) => normalizeLayoutItem(savedById.get(fallback.i), fallback));
  }

  return next;
}

function resolveStorage(storage?: Storage): Storage | null {
  if (storage) {
    return storage;
  }

  if (typeof window !== "undefined" && typeof window.localStorage !== "undefined") {
    return window.localStorage;
  }

  return null;
}

export function loadFinancialDashboardLayouts(storage?: Storage): FinancialDashboardLayouts {
  const target = resolveStorage(storage);
  if (!target) {
    return cloneLayouts(defaultFinancialDashboardLayouts);
  }

  try {
    const raw = target.getItem(FINANCIAL_DASHBOARD_LAYOUT_STORAGE_KEY);
    if (!raw) {
      return cloneLayouts(defaultFinancialDashboardLayouts);
    }

    return mergeFinancialDashboardLayouts(JSON.parse(raw) as FinancialDashboardLayouts);
  } catch {
    return cloneLayouts(defaultFinancialDashboardLayouts);
  }
}

export function saveFinancialDashboardLayouts(layouts: FinancialDashboardLayouts, storage?: Storage) {
  const target = resolveStorage(storage);
  if (!target) {
    return;
  }

  target.setItem(FINANCIAL_DASHBOARD_LAYOUT_STORAGE_KEY, JSON.stringify(mergeFinancialDashboardLayouts(layouts)));
}

export function resetFinancialDashboardLayouts(storage?: Storage): FinancialDashboardLayouts {
  const target = resolveStorage(storage);
  target?.removeItem(FINANCIAL_DASHBOARD_LAYOUT_STORAGE_KEY);
  return cloneLayouts(defaultFinancialDashboardLayouts);
}