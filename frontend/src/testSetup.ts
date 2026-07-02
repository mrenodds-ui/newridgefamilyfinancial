import "@testing-library/jest-dom/vitest";

// Mock ResizeObserver for jsdom (used by some chart/layout components).
if (typeof global.ResizeObserver === "undefined") {
  global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}

// assistant-ui thread viewport auto-scroll uses scrollTo in jsdom tests.
if (typeof HTMLElement !== "undefined" && !HTMLElement.prototype.scrollTo) {
  HTMLElement.prototype.scrollTo = () => {};
}
