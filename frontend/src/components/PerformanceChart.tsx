import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

interface Props {
  history: { run_ref: string; health_score: number; created_at: string }[];
}

const PerformanceChart: React.FC<Props> = ({ history }) => {
  if (!history || history.length === 0) return null;
  const data = history.map((h) => ({
    ref: h.run_ref,
    health: h.health_score,
    time: new Date(h.created_at).toLocaleDateString(),
  }));

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="font-semibold text-gray-800 mb-3">📈 Model Health Over Time</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="ref" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="health" stroke="#14b8a6" strokeWidth={2} name="Health score" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PerformanceChart;