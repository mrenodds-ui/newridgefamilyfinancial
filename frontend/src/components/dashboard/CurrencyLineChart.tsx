import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatCurrency, formatMonthLabel } from "../../../utils/formatting";

type ChartDatum = Record<string, string | number | null | undefined>;

export function CurrencyLineChart({
  data,
  lines,
  height = 320,
  legend = true,
}: {
  data: ChartDatum[];
  lines: { dataKey: string; name: string; color: string }[];
  height?: number;
  legend?: boolean;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 16, right: 24, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="rgba(116, 156, 255, 0.12)" strokeDasharray="2 6" vertical={false} />
        <XAxis
          dataKey="date"
          stroke="#8EA6D9"
          tick={{ fontSize: 11, fill: "#A7B9DD" }}
          tickFormatter={formatMonthLabel}
          interval="preserveStartEnd"
          minTickGap={24}
          tickLine={false}
          axisLine={false}
        />
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
          labelFormatter={formatMonthLabel}
        />
        {legend ? (
          <Legend
            wrapperStyle={{ color: "#90A4CB", fontSize: 11, fontFamily: "var(--font-mono)", paddingTop: 6 }}
            iconType="circle"
            align="right"
            verticalAlign="top"
            height={28}
          />
        ) : null}
        {lines.map((line) => (
          <Line
            key={line.dataKey}
            type="monotone"
            dataKey={line.dataKey}
            name={line.name}
            stroke={line.color}
            strokeWidth={3}
            strokeLinecap="round"
            strokeLinejoin="round"
            dot={false}
            activeDot={{ r: 4.5, stroke: "#E8F5FF", strokeWidth: 2, fill: line.color }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
