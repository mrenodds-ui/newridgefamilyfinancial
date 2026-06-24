import ImportPanel from "../components/dashboard/ImportPanel";

export default function ImportsPage() {
  return (
    <div className="dashboard-page">
      <div className="page-content">
        <header className="page-header">
          <p className="eyebrow">Practice Files</p>
          <h1>Bring In Files</h1>
          <p>Add the latest SoftDent and QuickBooks exports to refresh the dashboard.</p>
        </header>
        <ImportPanel />
      </div>
    </div>
  );
}
