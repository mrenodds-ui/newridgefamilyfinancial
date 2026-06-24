import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export function PatientFlowChart({
  data,
}: {
  data: { date: string; newPatients: number; returningPatients: number }[];
}) {
  return (
    <section className="dashboard-patient-flow">
      <h3 className="dashboard-section-title">Patient Flow</h3>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} margin={{ top: 16, right: 24, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(116, 156, 255, 0.16)" />
          <XAxis dataKey="date" stroke="#8EA6D9" tick={{ fontSize: 12, fill: "#D8E5FF" }} />
          <YAxis stroke="#8EA6D9" tick={{ fill: "#D8E5FF" }} />
          <Tooltip
            contentStyle={{
              background: "#0C1530",
              color: "#EDF4FF",
              borderRadius: 12,
              border: "1.5px solid #64A9FF",
              boxShadow: "0 16px 36px rgba(2, 8, 24, 0.36)",
            }}
            labelStyle={{ color: "#7EE1FF" }}
          />
          <Legend wrapperStyle={{ color: "#CFE0FF" }} iconType="rect" />
          <Bar dataKey="newPatients" fill="#72D6FF" name="New Patients" radius={[8, 8, 2, 2]} />
          <Bar dataKey="returningPatients" fill="#4C84FF" name="Returning Patients" radius={[8, 8, 2, 2]} />
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
}
