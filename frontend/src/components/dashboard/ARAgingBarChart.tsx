import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatCurrency } from "../../../utils/formatting";

const AR_COLORS = ["#7EE1FF", "#66AFFF", "#4C84FF", "#8BA4FF"];

export function ARAgingBarChart({ data, height = 320 }: { data: { name: string; value: number }[]; height?: number }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 16, right: 24, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="rgba(116, 156, 255, 0.12)" strokeDasharray="2 6" vertical={false} />
        <XAxis dataKey="name" stroke="#8EA6D9" tick={{ fontSize: 11, fill: "#A7B9DD" }} tickLine={false} axisLine={false} />
        <YAxis
          stroke="#8EA6D9"
          tickFormatter={formatCurrency}
          tick={{ fontSize: 11, fill: "#A7B9DD" }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip
          contentStyle={{
            background: "rgba(7, 12, 24, 0.96)",
            color: "#EDF4FF",
            borderRadius: 16,
            border: "1px solid rgba(120, 157, 255, 0.28)",
            boxShadow: "0 24px 48px rgba(2, 8, 24, 0.42)",
          }}
          labelStyle={{ color: "#7EE1FF" }}
          formatter={formatCurrency}
        />
        <Bar dataKey="value" isAnimationActive={false} barSize={24} radius={[999, 999, 4, 4]}>
          {data.map((entry, idx) => (
            <Cell key={entry.name} fill={AR_COLORS[idx % AR_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
