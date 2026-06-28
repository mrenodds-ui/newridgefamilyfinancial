import "@testing-library/jest-dom/vitest";

// Mock ResizeObserver for jsdom (used by some chart/layout components).
if (typeof global.ResizeObserver === "undefined") {
  global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}
