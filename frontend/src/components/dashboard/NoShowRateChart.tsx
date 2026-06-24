import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function NoShowRateChart({ data }: { data: { date: string; noShowRate: number }[] }) {
  return (
    <section className="dashboard-no-show-rate">
      <h3 className="dashboard-section-title">No-Show Rate Trend</h3>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data} margin={{ top: 16, right: 24, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(116, 156, 255, 0.16)" />
          <XAxis dataKey="date" stroke="#8EA6D9" tick={{ fontSize: 12, fill: "#D8E5FF" }} />
          <YAxis stroke="#8EA6D9" tickFormatter={(v) => `${v}%`} tick={{ fill: "#D8E5FF" }} />
          <Tooltip
            contentStyle={{
              background: "#0C1530",
              color: "#EDF4FF",
              borderRadius: 12,
              border: "1.5px solid #64A9FF",
              boxShadow: "0 16px 36px rgba(2, 8, 24, 0.36)",
            }}
            labelStyle={{ color: "#7EE1FF" }}
            formatter={(v: number) => `${v}%`}
          />
          <Line type="monotone" dataKey="noShowRate" stroke="#72D6FF" strokeWidth={3.25} dot={false} activeDot={{ r: 4, stroke: "#E8F5FF", strokeWidth: 2, fill: "#72D6FF" }} />
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}
