import type { SoftDentCoverageSummary } from "../../api/client";

function coverageBadgeClass(status: "missing" | "limited" | "available") {
  if (status === "missing") {
    return "dashboard-import-status-badge dashboard-import-status-badge--error";
  }
  if (status === "limited") {
    return "dashboard-import-status-badge dashboard-import-status-badge--pending";
  }
  return "dashboard-import-status-badge";
}

function coverageBadgeLabel(status: "missing" | "limited" | "available") {
  if (status === "missing") {
    return "needed";
  }
  if (status === "limited") {
    return "partial";
  }
  return "ready";
}

type SoftDentCoveragePanelProps = {
  coverage?: SoftDentCoverageSummary | null;
  emptyMessage: string;
};

export function SoftDentCoveragePanel({ coverage, emptyMessage }: SoftDentCoveragePanelProps) {
  if (!coverage) {
    return <div className="hal-answer-card">{emptyMessage}</div>;
  }

  return (
    <>
      <div className="admin-audit-item__summary">{coverage.summary}</div>
      <div className="admin-audit-item__summary">
        <span className="dashboard-import-status-badge dashboard-import-status-badge--error dashboard-import-status-badge--spaced">
          Needed: {coverage.counts.missing}
        </span>
        <span className="dashboard-import-status-badge dashboard-import-status-badge--pending dashboard-import-status-badge--spaced">
          Partial: {coverage.counts.limited}
        </span>
        <span className="dashboard-import-status-badge dashboard-import-status-badge--spaced">Ready: {coverage.counts.available}</span>
      </div>
      <table className="import-history-table">
        <thead>
          <tr>
            <th>Report</th>
            <th>Status</th>
            <th>File</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {(coverage.rows ?? []).map((row) => (
            <tr key={row.key}>
              <td>{row.label}</td>
              <td>
                <span className={coverageBadgeClass(row.status)}>{coverageBadgeLabel(row.status)}</span>
              </td>
              <td>
                <div>{row.sourceFile || row.requiredReport}</div>
                <div>{row.sourceBackend !== "missing" ? row.sourceBackend.replaceAll("_", " ") : "file needed"}</div>
                {row.lastPeriod ? <div>Latest period: {row.lastPeriod}</div> : null}
                {row.rowCount > 0 ? <div>Rows: {row.rowCount}</div> : null}
              </td>
              <td>
                <div>{row.summary}</div>
                <div>
                  <strong>Next step:</strong> {row.action}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
