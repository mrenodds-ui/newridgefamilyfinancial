import { Bar, BarChart, Cell, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatCurrency } from "../../../utils/formatting";

const COLORS = ["#7EE1FF", "#66AFFF", "#4C84FF", "#5B74FF", "#72D6FF", "#8BA4FF"];

type HorizontalExpenseBarDatum = {
  category: string;
  amount: number;
};

export function HorizontalExpenseBarChart({ data, height = 320 }: { data: HorizontalExpenseBarDatum[]; height?: number }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ top: 16, right: 24, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="rgba(116, 156, 255, 0.12)" strokeDasharray="2 6" horizontal={false} />
        <XAxis
          type="number"
          stroke="#8EA6D9"
          tickFormatter={formatCurrency}
          tick={{ fontSize: 11, fill: "#A7B9DD" }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          dataKey="category"
          type="category"
          stroke="#8EA6D9"
          tick={{ fontSize: 11, fill: "#D8E5FF" }}
          width={108}
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
        <Bar dataKey="amount" barSize={16} radius={[0, 999, 999, 0]}>
          {data.map((entry, idx) => (
            <Cell key={entry.category} fill={COLORS[idx % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
