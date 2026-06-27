import ImportPanel from "../components/dashboard/ImportPanel";
import { PageSurfaceHeader, PageSurfaceShell } from "../components/PageSurfaceHeader";

export default function ImportsPage() {
  return (
    <PageSurfaceShell className="imports-page">
      <PageSurfaceHeader
        breadcrumbs="Data sources / Imports"
        eyebrow="Practice file intake"
        title="Bring in files"
        titleId="imports-page-title"
        description="Stage SoftDent and QuickBooks exports through the backend import pipeline. Admin accounts upload files; everyone with dashboard access can review live import status and coverage."
        badges={[
          { label: "Admin Upload Only", tone: "warning" },
          { label: "Backend Normalized" },
          { label: "No Writeback" },
        ]}
        badgesAriaLabel="Import pipeline safety posture"
      />
      <div className="page-content">
        <ImportPanel />
      </div>
    </PageSurfaceShell>
  );
}
