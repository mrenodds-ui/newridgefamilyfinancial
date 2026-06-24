import { describe, expect, it } from "vitest";

import {
  FINANCIAL_DASHBOARD_LAYOUT_STORAGE_KEY,
  defaultFinancialDashboardLayouts,
  loadFinancialDashboardLayouts,
  mergeFinancialDashboardLayouts,
  resetFinancialDashboardLayouts,
  saveFinancialDashboardLayouts,
} from "../components/dashboard/financialDashboardLayout";

describe("financialDashboardLayout", () => {
  it("falls back to the default layouts when storage is empty or invalid", () => {
    window.localStorage.removeItem(FINANCIAL_DASHBOARD_LAYOUT_STORAGE_KEY);
    expect(loadFinancialDashboardLayouts(window.localStorage)).toEqual(defaultFinancialDashboardLayouts);

    window.localStorage.setItem(FINANCIAL_DASHBOARD_LAYOUT_STORAGE_KEY, "not-json");
    expect(loadFinancialDashboardLayouts(window.localStorage)).toEqual(defaultFinancialDashboardLayouts);
  });

  it("merges saved positions with the default tile set", () => {
    const merged = mergeFinancialDashboardLayouts({
      lg: [
        {
          i: "featured",
          x: 4,
          y: 1,
          w: 8,
          h: 6,
        },
      ],
    });

    const featured = merged.lg?.find((item) => item.i === "featured");
    const paymentMix = merged.lg?.find((item) => item.i === "payment-mix");

    expect(featured).toMatchObject({ x: 4, y: 1, w: 8, h: 6 });
    expect(paymentMix).toBeDefined();
    expect(merged.lg).toHaveLength(defaultFinancialDashboardLayouts.lg?.length ?? 0);
  });

  it("saves normalized layouts and resets back to defaults", () => {
    const custom = mergeFinancialDashboardLayouts({
      lg: [
        {
          i: "case-acceptance",
          x: 2,
          y: 3,
          w: 6,
          h: 5,
        },
      ],
    });

    saveFinancialDashboardLayouts(custom, window.localStorage);

    expect(loadFinancialDashboardLayouts(window.localStorage).lg?.find((item) => item.i === "case-acceptance")).toMatchObject({
      x: 2,
      y: 3,
      w: 6,
      h: 5,
    });

    const reset = resetFinancialDashboardLayouts(window.localStorage);
    expect(window.localStorage.getItem(FINANCIAL_DASHBOARD_LAYOUT_STORAGE_KEY)).toBeNull();
    expect(reset).toEqual(defaultFinancialDashboardLayouts);
  });
});