import type { ReactNode } from "react";

interface ChartCardProps {
  title: string;
  children: ReactNode;
}

export function ChartCard({ title, children }: ChartCardProps) {
  return (
    <section className="dashboard-chart-card">
      <div className="dashboard-chart-title">{title}</div>
      {children}
    </section>
  );
}
