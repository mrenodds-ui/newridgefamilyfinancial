import "./MissionControlMockupPage.css";

type MockupPageKey = "financial" | "softdent" | "quickbooks" | "ar" | "claims" | "narratives" | "documents" | "library" | "hal";

type MetricTile = {
  label: string;
  value: string;
  detail?: string;
  tone?: "gold" | "cyan" | "sage" | "red";
};

type MockupPageConfig = {
  eyebrow: string;
  title: string;
  subtitle: string;
  chips: string[];
  heroMetric: MetricTile;
  metrics: MetricTile[];
};

const PAGE_CONFIG: Record<MockupPageKey, MockupPageConfig> = {
  financial: {
    eyebrow: "Owner financial dashboard",
    title: "Production command view",
    subtitle: "Executive bento dashboard for production, collections, A/R, EBITDA, payer mix, and provider performance.",
    chips: ["Operational", "Read-only review", "Data freshness locked"],
    heroMetric: { label: "Production MTD", value: "$116,780", detail: "+8.4% vs prior period", tone: "sage" },
    metrics: [
      { label: "Collections", value: "$107,015", detail: "92% pace", tone: "sage" },
      { label: "Net A/R", value: "$73,144", detail: "DAYSHEET imported", tone: "cyan" },
      { label: "EBITDA margin", value: "18.6%", detail: "Owner view", tone: "gold" },
    ],
  },
  softdent: {
    eyebrow: "SoftDent source",
    title: "DAYSHEET A/R — Imported",
    subtitle: "Read-only source-of-truth page for practice production, collections, insurance-vs-patient A/R, and export health.",
    chips: ["Read-only", "DAYSHEET imported", "No writeback"],
    heroMetric: { label: "DAYSHEET A/R", value: "$73,144", detail: "Imported read-only", tone: "cyan" },
    metrics: [
      { label: "Production total", value: "$116,780", tone: "gold" },
      { label: "Collection total", value: "$107,015", tone: "sage" },
      { label: "Source health", value: "Fresh", detail: "Last import verified", tone: "cyan" },
    ],
  },
  quickbooks: {
    eyebrow: "QuickBooks source",
    title: "Profit & Loss summary",
    subtitle: "Accountant-grade P&L cockpit for revenue, expenses, net income, EBITDA candidates, and read-only sync status.",
    chips: ["Read-only sync", "P&L summary", "Owner review"],
    heroMetric: { label: "Net income", value: "$34,920", detail: "Current period", tone: "sage" },
    metrics: [
      { label: "Revenue", value: "$148,600", tone: "gold" },
      { label: "Expenses", value: "$113,680", tone: "red" },
      { label: "EBITDA candidates", value: "7", detail: "Review lines", tone: "cyan" },
    ],
  },
  ar: {
    eyebrow: "A/R & collections",
    title: "Total outstanding A/R",
    subtitle: "Operational collections board with aging buckets, top outstanding claims, collection trend, and follow-up readiness.",
    chips: ["SoftDent read-only", "No payer contact", "Not submitted"],
    heroMetric: { label: "Total Outstanding A/R", value: "$73,144", detail: "Aging gradient active", tone: "red" },
    metrics: [
      { label: "0-30 days", value: "$41,020", tone: "sage" },
      { label: "31-60 days", value: "$18,400", tone: "gold" },
      { label: "90+ days", value: "$7,880", tone: "red" },
    ],
  },
  claims: {
    eyebrow: "Patient claims workbench",
    title: "Claims pipeline",
    subtitle: "Review-only claim board with Draft, Needs Review, Ready, and Denied lanes plus selected claim detail.",
    chips: ["Local-only", "Human review required", "No payer submission"],
    heroMetric: { label: "Claims in review", value: "24", detail: "Across four lanes", tone: "gold" },
    metrics: [
      { label: "Ready", value: "9", tone: "sage" },
      { label: "Needs review", value: "11", tone: "gold" },
      { label: "Blocked/Denied", value: "4", tone: "red" },
    ],
  },
  narratives: {
    eyebrow: "Insurance narratives",
    title: "Generate narrative",
    subtitle: "Two-pane draft workspace: composer on the left, draft narrative preview and source facts on the right.",
    chips: ["Draft only", "Human review required", "No SoftDent writeback"],
    heroMetric: { label: "Draft status", value: "Ready for review", detail: "Not submitted", tone: "sage" },
    metrics: [
      { label: "Source facts", value: "12", tone: "cyan" },
      { label: "Missing data notes", value: "3", tone: "gold" },
      { label: "Draft history", value: "8", tone: "sage" },
    ],
  },
  documents: {
    eyebrow: "Accounting documents",
    title: "Document intake & posting queue",
    subtitle: "Accounting operations board for extraction, posting status, journal drafts, and period review.",
    chips: ["Review-gated", "Extracted fields", "Journal draft only"],
    heroMetric: { label: "Documents queued", value: "18", detail: "Pending staff review", tone: "gold" },
    metrics: [
      { label: "Approved", value: "7", tone: "sage" },
      { label: "Needs review", value: "9", tone: "gold" },
      { label: "Blocked", value: "2", tone: "red" },
    ],
  },
  library: {
    eyebrow: "Document library",
    title: "Read-only repository",
    subtitle: "Searchable knowledge-base layout with category chips, document cards, preview rail, and indexed count.",
    chips: ["Policies", "Statements", "Claims", "Clinical", "Reports"],
    heroMetric: { label: "Indexed documents", value: "142", detail: "Read-only", tone: "cyan" },
    metrics: [
      { label: "Policies", value: "28", tone: "cyan" },
      { label: "Claims", value: "46", tone: "gold" },
      { label: "Clinical", value: "31", tone: "sage" },
    ],
  },
  hal: {
    eyebrow: "HAL command center",
    title: "Ask HAL",
    subtitle: "Mission-control AI surface with source intake, local reasoning core, staff work surfaces, and external-action firewall.",
    chips: ["Local-only", "Read-only sources", "Human review required", "Not submitted"],
    heroMetric: { label: "Local packets", value: "36", detail: "Ready / Needs-review / Blocked", tone: "gold" },
    metrics: [
      { label: "Ready", value: "18", tone: "sage" },
      { label: "Needs review", value: "14", tone: "gold" },
      { label: "Blocked", value: "4", tone: "red" },
    ],
  },
};

const LANES = [
  { title: "Draft", tone: "gold", cards: ["Delta Dental crown", "Cigna ortho note", "Aetna missing x-ray"] },
  { title: "Needs Review", tone: "gold", cards: ["MetLife appeal", "BCBS attachment", "Guardian payer note"] },
  { title: "Ready", tone: "sage", cards: ["UHC claim packet", "Principal perio narrative"] },
  { title: "Denied", tone: "red", cards: ["Denied crown review", "Payer contact blocked"] },
];

const DOCUMENTS = [
  "Clinical note packet",
  "June bank statement",
  "Payer policy PDF",
  "Crown claim images",
  "AP invoice scan",
  "Monthly report",
];
const SPARKLINE_BARS = Array.from({ length: 18 }, (_, index) => ({
  id: `spark-${index + 1}`,
  height: `${28 + ((index * 17) % 48)}%`,
}));
const BAR_CHART_BARS = [
  { id: "bar-1", height: "92%" },
  { id: "bar-2", height: "74%" },
  { id: "bar-3", height: "86%" },
  { id: "bar-4", height: "61%" },
  { id: "bar-5", height: "78%" },
];

function Metric({ tile }: { tile: MetricTile }) {
  return (
    <article className={`mc-metric mc-metric--${tile.tone ?? "cyan"}`}>
      <span>{tile.label}</span>
      <strong>{tile.value}</strong>
      {tile.detail ? <p>{tile.detail}</p> : null}
    </article>
  );
}

function Sparkline() {
  return (
    <div className="mc-sparkline" aria-hidden="true">
      {SPARKLINE_BARS.map((bar) => (
        <span key={bar.id} style={{ height: bar.height }} />
      ))}
    </div>
  );
}

function Donut() {
  return (
    <div className="mc-donut" aria-label="Payer mix donut">
      <span>68%</span>
    </div>
  );
}

function Bars() {
  return (
    <div className="mc-bars" aria-hidden="true">
      {BAR_CHART_BARS.map((bar) => (
        <span key={bar.id} style={{ height: bar.height }} />
      ))}
    </div>
  );
}

function ClaimsBoard() {
  return (
    <section className="mc-card mc-card--wide">
      <div className="mc-card__head">
        <span>Claims pipeline</span>
        <strong>Draft / Needs Review / Ready / Denied</strong>
      </div>
      <div className="mc-kanban">
        {LANES.map((lane) => (
          <div key={lane.title} className={`mc-lane mc-lane--${lane.tone}`}>
            <div className="mc-lane__title">
              <span>{lane.title}</span>
              <strong>{lane.cards.length}</strong>
            </div>
            {lane.cards.map((card) => (
              <article key={card}>{card}</article>
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}

function NarrativeComposer() {
  return (
    <section className="mc-two-pane">
      <article className="mc-card">
        <div className="mc-card__head">
          <span>Generate narrative</span>
          <strong>Composer</strong>
        </div>
        <div className="mc-form-line">Patient / claim: CLAIM-1001</div>
        <div className="mc-form-line">Procedure: Crown restoration</div>
        <div className="mc-form-area">Clinical context, source facts, missing-data notes...</div>
        <button className="mc-button" type="button">
          Prepare draft for review
        </button>
      </article>
      <article className="mc-card">
        <div className="mc-card__head">
          <span>Draft narrative</span>
          <strong>Preview</strong>
        </div>
        <div className="mc-banner">Draft only — requires human review</div>
        <p className="mc-doc-copy">
          Patient presents with clinical documentation supporting medical necessity. Source references are attached for staff review before
          any submission.
        </p>
        <div className="mc-source-list">
          <span>Clinical note ref</span>
          <span>Procedure code ref</span>
          <span>Missing attachment note</span>
        </div>
      </article>
    </section>
  );
}

function DocumentGrid() {
  return (
    <section className="mc-doc-grid">
      {DOCUMENTS.map((document) => (
        <article key={document} className="mc-doc-card">
          <span className="mc-doc-card__icon">PDF</span>
          <strong>{document}</strong>
          <p>Read-only · Indexed · Source referenced</p>
        </article>
      ))}
      <article className="mc-card mc-card--preview">
        <div className="mc-card__head">
          <span>Document preview</span>
          <strong>Selected file</strong>
        </div>
        <div className="mc-preview-sheet" />
      </article>
    </section>
  );
}

function SourceTable({ page }: { page: MockupPageKey }) {
  const rows =
    page === "documents"
      ? ["Vendor invoice · Needs review · $1,420", "Bank statement · Approved · $8,210", "Receipt packet · Pending · $640"]
      : ["SoftDent export · Fresh · Read-only", "QuickBooks summary · Synced · Read-only", "DAYSHEET import · Verified · Read-only"];

  return (
    <section className="mc-card mc-card--wide">
      <div className="mc-card__head">
        <span>{page === "documents" ? "Document intake & posting queue" : "Recent source exports"}</span>
        <strong>Review queue</strong>
      </div>
      <div className="mc-table">
        {rows.map((row) => (
          <div key={row}>
            <span>{row}</span>
            <strong>Review</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function HalTopology() {
  return (
    <section className="mc-hal-map">
      <article className="mc-card">
        <div className="mc-card__head">
          <span>Read-only source intake</span>
          <strong>Local feeds</strong>
        </div>
        {["SoftDent A/R", "Claims export", "Local tasks", "Local packets"].map((item) => (
          <div className="mc-feed" key={item}>
            {item}
            <span>READ-ONLY</span>
          </div>
        ))}
      </article>
      <article className="mc-core">
        <span>HAL</span>
        <strong>Local reasoning core</strong>
      </article>
      <article className="mc-card">
        <div className="mc-card__head">
          <span>External action firewall</span>
          <strong>Blocked</strong>
        </div>
        {["No Email", "No Fax", "No Upload", "No Payer Contact", "No Writeback"].map((item) => (
          <div className="mc-firewall" key={item}>
            {item}
          </div>
        ))}
      </article>
    </section>
  );
}

function MainBody({ page }: { page: MockupPageKey }) {
  if (page === "claims") return <ClaimsBoard />;
  if (page === "narratives") return <NarrativeComposer />;
  if (page === "library") return <DocumentGrid />;
  if (page === "hal") return <HalTopology />;

  return (
    <>
      <section className="mc-chart-grid">
        <article className="mc-card mc-card--wide">
          <div className="mc-card__head">
            <span>{page === "ar" ? "Collections trend" : "Trailing 12-month production vs collections"}</span>
            <strong>Live view</strong>
          </div>
          <Sparkline />
        </article>
        <article className="mc-card">
          <div className="mc-card__head">
            <span>{page === "quickbooks" ? "Expense categories" : "Payer mix"}</span>
            <strong>{page === "quickbooks" ? "Bars" : "Donut"}</strong>
          </div>
          {page === "quickbooks" ? <Bars /> : <Donut />}
        </article>
        <article className="mc-card">
          <div className="mc-card__head">
            <span>{page === "ar" ? "Aging buckets" : "Provider production"}</span>
            <strong>Ranked</strong>
          </div>
          <Bars />
        </article>
      </section>
      <SourceTable page={page} />
    </>
  );
}

export function MissionControlMockupPage({ page }: { page: MockupPageKey }) {
  const config = PAGE_CONFIG[page];

  return (
    <main className={`mc-page mc-page--${page}`}>
      <section className="mc-hero">
        <div className="mc-hero__copy">
          <p className="mc-eyebrow">{config.eyebrow}</p>
          <h1>{config.title}</h1>
          <p>{config.subtitle}</p>
          <div className="mc-chip-row">
            {config.chips.map((chip) => (
              <span key={chip}>{chip}</span>
            ))}
          </div>
        </div>
        <Metric tile={config.heroMetric} />
      </section>

      <section className="mc-metric-grid">
        {config.metrics.map((metric) => (
          <Metric key={metric.label} tile={metric} />
        ))}
      </section>

      <MainBody page={page} />
    </main>
  );
}
