import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = join(__dirname, "..");
const require = createRequire(import.meta.url);

process.env.NR2_LOAD_IMPORTS = "1";

const HalSkills = require(join(projectRoot, "site", "hal-skills.js"));
const Services = require(join(projectRoot, "site", "services.js"));

const snap = await Services.readProgramSnapshot();
const feed = HalSkills.buildWidgetFeed(snap);
console.log(
  JSON.stringify(
    {
      overview: feed.widgets.practiceFinancialOverview?.status,
      quality: feed.widgets.dataFreshnessQuality?.metrics?.qualityScore,
      validation: feed.accountingExcelValidation?.status,
      arCross: snap.dashboards?.financial?.arCrossCheck ?? null,
      expenseScope: snap.dashboards?.quickbooks?.expenseCategories?.scopeLabel ?? null,
      issues: (feed.accountingExcelValidation?.issues ?? []).slice(0, 6),
    },
    null,
    2,
  ),
);
