/**
 * Node parity tests for import-diagnostics checksum detection.
 */
import assert from "node:assert/strict";
import ImportDiagnostics from "./site/import-diagnostics.js";

const { evaluateDataset, STATUS } = ImportDiagnostics;

const contract = {
  system: "softdent",
  bundleKey: "dashboard",
  automated: true,
  severity: "critical",
  freshnessMaxMinutes: 1440,
  requiredFields: ["production"],
  fieldAliases: { production: ["production"] },
};

const rows = [
  { production: 100, period: "2026-06" },
  { production: 90, period: "2026-05" },
];

const changed = evaluateDataset(
  "softdent.dashboard",
  contract,
  {
    sourceFile: "softdent_dashboard_data.json",
    modifiedAt: "2026-06-30T12:00:00.000Z",
    sha256: "bbbb",
    rows,
  },
  { datasets: { "softdent.dashboard": contract } },
  [],
  {
    "softdent.dashboard": {
      sourceFile: "softdent_dashboard_data.json",
      sha256: "aaaa",
    },
  },
);
assert.equal(changed.status, STATUS.PARTIAL);
assert.equal(changed.checksumChanged, true);
assert.match(changed.detail, /checksum/i);

const stable = evaluateDataset(
  "softdent.dashboard",
  contract,
  {
    sourceFile: "softdent_dashboard_data.json",
    modifiedAt: "2026-06-30T12:00:00.000Z",
    sha256: "same-hash",
    rows,
  },
  { datasets: { "softdent.dashboard": contract } },
  [],
  {
    "softdent.dashboard": {
      sourceFile: "softdent_dashboard_data.json",
      sha256: "same-hash",
    },
  },
);
assert.equal(stable.status, STATUS.CONNECTED);
assert.equal(stable.checksumChanged, false);

console.log("test_import_diagnostics_node.mjs: ok");
