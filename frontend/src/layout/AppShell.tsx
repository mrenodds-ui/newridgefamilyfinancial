import Sidebar from "./Sidebar";
import "../theme.css";

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell app-shell--dashboard-theme">
      <aside className="app-sidebar">
        <Sidebar />
      </aside>
      <main className="app-main">
        <div className="page-content">
          {children}
        </div>
      </main>
    </div>
  );
}
