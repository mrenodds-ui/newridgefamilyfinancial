import { useMemo } from "react";
import { useLocation } from "react-router-dom";

export type HalPageContext = {
  route: string;
  pageTitle: string;
  capturedAt: string;
};

/** Safe frontend-only page context for future HAL backend wiring. Not transmitted yet. */
export function useHalPageContext(): HalPageContext {
  const location = useLocation();

  return useMemo(
    () => ({
      route: `${location.pathname}${location.search}${location.hash}`,
      pageTitle: typeof document !== "undefined" ? document.title : "",
      capturedAt: new Date().toISOString(),
    }),
    [location.pathname, location.search, location.hash],
  );
}
