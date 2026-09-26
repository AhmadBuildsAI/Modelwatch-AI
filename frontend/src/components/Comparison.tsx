import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { listModels, compareVersions } from '../services/monitoring';
import { ModelListItem, ComparisonRow } from '../types';

const Comparison: React.FC = () => {
  const navigate = useNavigate();
  const [models, setModels] = useState<ModelListItem[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [rows, setRows] = useState<ComparisonRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listModels()
      .then((ms) => {
        setModels(ms);
        if (ms.length > 0) setSelectedModel(ms[0].id);
      })
      .catch(() => toast.error('Failed to load models'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedModel) return;
    compareVersions(selectedModel)
      .then(setRows)
      .catch(() => toast.error('Failed to compare'));
  }, [selectedModel]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Model Comparison</h1>
        <p className="text-gray-500 text-sm">Compare monitoring results across versions</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <label className="block text-sm font-medium text-gray-700 mb-1">Select Model</label>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="w-full max-w-md rounded-lg border border-gray-300 px-3 py-2"
          disabled={loading}
        >
          {models.map((m) => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>
      </div>

      {rows.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500">
          No version data available.
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
              <tr>
                <th className="px-4 py-3 text-left">Version</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Training Date</th>
                <th className="px-4 py-3 text-left">Baseline F1</th>
                <th className="px-4 py-3 text-left">Latest Health</th>
                <th className="px-4 py-3 text-left">Latest Drift</th>
                <th className="px-4 py-3 text-left">Retrain?</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {rows.map((r) => (
                <tr key={r.version} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{r.version}</td>
                  <td className="px-4 py-3 capitalize">{r.status}</td>
                  <td className="px-4 py-3 text-gray-600">{r.training_date}</td>
                  <td className="px-4 py-3">{r.baseline_f1?.toFixed(3) ?? '—'}</td>
                  <td className="px-4 py-3">{r.latest_health_score?.toFixed(0) ?? '—'}</td>
                  <td className="px-4 py-3">{r.latest_overall_drift ?? '—'}</td>
                  <td className="px-4 py-3">{r.retraining_recommended ? '⚠️ Yes' : '✓ No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Comparison;