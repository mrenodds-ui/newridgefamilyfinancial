import { Navigate, Route, Routes } from "react-router-dom";
import { MissionControlMockupPage } from "./components/mockup/MissionControlMockupPage";
import AppShell from "./layout/AppShell";

const HAL_DASHBOARD_PATH = "/dashboard/hal";

// All routes render static mission-control mockups with no sign-in gate.
export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<MissionControlMockupPage page="financial" />} />
        <Route path="/softdent" element={<MissionControlMockupPage page="softdent" />} />
        <Route path="/quickbooks" element={<MissionControlMockupPage page="quickbooks" />} />
        <Route path="/imports" element={<MissionControlMockupPage page="softdent" />} />
        <Route path="/ebitda" element={<MissionControlMockupPage page="quickbooks" />} />
        <Route path="/expenses" element={<MissionControlMockupPage page="quickbooks" />} />
        <Route path="/ar" element={<MissionControlMockupPage page="ar" />} />
        <Route path="/trends" element={<MissionControlMockupPage page="financial" />} />
        <Route path="/admin" element={<MissionControlMockupPage page="financial" />} />
        <Route path="/claims-workbench" element={<MissionControlMockupPage page="claims" />} />
        <Route path="/accounting-documents" element={<MissionControlMockupPage page="documents" />} />
        <Route path="/document-library" element={<MissionControlMockupPage page="library" />} />
        <Route path="/accounting-policy" element={<MissionControlMockupPage page="documents" />} />
        <Route path="/posting-queue" element={<MissionControlMockupPage page="documents" />} />
        <Route path="/insurance-narratives" element={<MissionControlMockupPage page="narratives" />} />
        <Route path={HAL_DASHBOARD_PATH} element={<MissionControlMockupPage page="hal" />} />
        <Route path="/hal" element={<Navigate to={HAL_DASHBOARD_PATH} replace />} />
        <Route path="/hal-9000" element={<Navigate to={HAL_DASHBOARD_PATH} replace />} />
        <Route path="/hal-landing" element={<MissionControlMockupPage page="hal" />} />
        <Route path="/journal-draft" element={<MissionControlMockupPage page="documents" />} />
        <Route path="/settings" element={<MissionControlMockupPage page="financial" />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}
