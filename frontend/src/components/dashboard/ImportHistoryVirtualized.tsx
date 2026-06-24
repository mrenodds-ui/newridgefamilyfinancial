import type { ImportRecord } from "../../types/dashboard";
import "./importpanel.css";
import "./importhistoryvirtualized.css";

function displaySource(source: string) {
  if (source === "softdent") {
    return "SoftDent";
  }
  if (source === "quickbooks") {
    return "QuickBooks";
  }
  return source;
}

function displayStatus(status: string) {
  if (status === "success") {
    return "Updated";
  }
  if (status === "pending") {
    return "Waiting";
  }
  if (status === "error") {
    return "Needs attention";
  }
  return status;
}

export default function ImportHistoryVirtualized({ history }: { history: ImportRecord[] }) {
  if (!history.length) {
    return <div className="import-history-empty">No file activity yet.</div>;
  }

  return (
    <section className="dashboard-import-history-card">
      <div className="dashboard-import-history-title">Recent File Activity</div>
      <div className="dashboard-import-table-scroll">
        {history.map((rec) => (
          <div key={rec.id} className="import-history-row">
            <span className="import-history-source">{displaySource(rec.source)}</span>
            <span className="import-history-type">{rec.reportType}</span>
            <span className="import-history-filename">{rec.fileName}</span>
            <span className="import-history-date">{new Date(rec.importedAt).toLocaleString()}</span>
            <span className="import-history-rows">{rec.rowCount}</span>
            <span className="import-history-status">{displayStatus(rec.status)}</span>
            <span className="import-history-error">{rec.errorMessage ? rec.errorMessage : "—"}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
