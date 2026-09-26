import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from 'recharts';
import toast from 'react-hot-toast';
import StatCard from './StatCard';
import { getDashboard } from '../services/monitoring';
import { DashboardData } from '../types';

const SEV_COLORS: Record<string, string> = {
  CRITICAL: 'bg-red-100 text-red-700',
  WARNING: 'bg-yellow-100 text-yellow-700',
  INFO: 'bg-blue-100 text-blue-700',
};

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch(() => toast.error('Failed to load dashboard'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>;
  if (!data) return null;

  const trend = (data.health_trend || []).map((h) => ({
    ref: h.run_ref,
    health: h.health_score,
  }));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Monitoring Dashboard</h1>
          <p className="text-gray-500 text-sm">
            Real-time visibility into deployed model health
          </p>
        </div>
        <Link
          to="/models"
          className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition"
        >
          🧠 View Models
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Models" value={data.total_models} icon="🧠" color="teal" />
        <StatCard title="Healthy" value={data.healthy} icon="✅" color="green" />
        <StatCard title="Warning" value={data.warning} icon="⚠️" color="yellow" />
        <StatCard title="Critical" value={data.critical} icon="🚨" color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-800 mb-3">Model Health Trend</h3>
          {trend.length === 0 ? (
            <p className="text-sm text-gray-500 py-12 text-center">
              No monitoring runs yet. Go to Models → run a monitoring pass.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="ref" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="health" stroke="#14b8a6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="font-semibold text-gray-800 mb-3">Recent Alerts</h3>
          {data.recent_alerts.length === 0 ? (
            <p className="text-sm text-gray-500">No alerts yet 🎉</p>
          ) : (
            <div className="space-y-2">
              {data.recent_alerts.map((a) => (
                <div key={a.id} className="border border-gray-100 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${SEV_COLORS[a.severity]}`}>
                      {a.severity}
                    </span>
                    <span className="text-xs text-gray-500 truncate">{a.model_name}</span>
                  </div>
                  <p className="text-sm text-gray-800">{a.title}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;