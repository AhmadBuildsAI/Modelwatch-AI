import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import StatCard from './StatCard';
import HealthGauge from './HealthGauge';
import DriftTable from './DriftTable';
import QualityPanel from './QualityPanel';
import RecommendationCard from './RecommendationCard';
import PerformanceChart from './PerformanceChart';
import { getModel, runMonitoring, getLatestRun, getRunHistory, compareVersions } from '../services/monitoring';
import { MonitoringRunResponse, ComparisonRow } from '../types';

const ModelDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [model, setModel] = useState<any>(null);
  const [run, setRun] = useState<MonitoringRunResponse | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [comparison, setComparison] = useState<ComparisonRow[]>([]);
  const [tab, setTab] = useState<'overview' | 'drift' | 'quality' | 'performance'>('overview');
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [driftIntensity, setDriftIntensity] = useState(0.3);

  const refresh = async () => {
    if (!id) return;
    try {
      const [m, h, c] = await Promise.all([
        getModel(id),
        getRunHistory(id).catch(() => []),
        compareVersions(id).catch(() => []),
      ]);
      setModel(m);
      setHistory(h);
      setComparison(c);
      try {
        const latest = await getLatestRun(id);
        setRun(latest);
      } catch {
        setRun(null);
      }
    } catch {
      toast.error('Failed to load model');
      navigate('/models');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, [id]);

  const handleRun = async () => {
    if (!id) return;
    setRunning(true);
    try {
      const r = await runMonitoring(id, driftIntensity);
      setRun(r);
      toast.success('Monitoring run complete');
      await refresh();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to run monitoring');
    } finally {
      setRunning(false);
    }
  };

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>;
  if (!model) return null;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">{model.name}</h1>
          <p className="text-gray-500 text-sm">
            {model.model_ref} · {model.task_type} {model.domain && `· ${model.domain}`}
          </p>
        </div>
        <button onClick={() => navigate('/models')} className="text-sm text-teal-600 hover:underline">
          ← Models
        </button>
      </div>

      {/* Run Control */}
      <div className="bg-white rounded-xl border border-gray-200 p-5">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Drift Intensity (0 = none, 1 = severe)
            </label>
            <input
              type="range" min={0} max={1} step={0.05}
              value={driftIntensity}
              onChange={(e) => setDriftIntensity(Number(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">Current: {driftIntensity.toFixed(2)}</p>
          </div>
          <button
            onClick={handleRun}
            disabled={running}
            className="px-6 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 disabled:opacity-50 font-semibold"
          >
            {running ? '⏳ Running...' : '▶ Run Monitoring'}
          </button>
        </div>
      </div>

      {run ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <HealthGauge score={run.health_score} status={run.health_status} />
            <StatCard
              title="Data Drift"
              value={run.overall_drift_level}
              color={run.overall_drift_level === 'HIGH' ? 'red' : run.overall_drift_level === 'MEDIUM' ? 'yellow' : 'green'}
              icon="📊"
            />
            <StatCard
              title="Prediction Drift"
              value={run.prediction_drift?.level ?? '—'}
              color={run.prediction_drift?.level === 'HIGH' ? 'red' : run.prediction_drift?.level === 'MEDIUM' ? 'yellow' : 'green'}
              icon="🎯"
            />
          </div>

          <div className="border-b border-gray-200">
            <div className="flex space-x-4">
              {[
                { key: 'overview', label: '📋 Overview' },
                { key: 'drift', label: `📊 Drift (${run.feature_drift.length})` },
                { key: 'quality', label: '🧹 Data Quality' },
                { key: 'performance', label: '📈 Performance' },
              ].map((t) => (
                <button
                  key={t.key}
                  onClick={() => setTab(t.key as any)}
                  className={`pb-2 px-1 text-sm font-medium transition ${
                    tab === t.key
                      ? 'border-b-2 border-teal-600 text-teal-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          {tab === 'overview' && (
            <div className="space-y-4">
              <div className="bg-white rounded-xl border border-gray-200 p-5">
                <h3 className="font-semibold text-gray-800 mb-3">🔍 Top Issues</h3>
                {run.top_issues.length === 0 ? (
                  <p className="text-sm text-green-600">✅ No significant issues detected</p>
                ) : (
                  <div className="space-y-2">
                    {run.top_issues.map((iss, i) => (
                      <div key={i} className={`border-l-4 pl-3 py-2 ${
                        iss.severity === 'HIGH' ? 'border-red-500 bg-red-50' :
                        iss.severity === 'MEDIUM' ? 'border-yellow-500 bg-yellow-50' :
                        'border-blue-500 bg-blue-50'
                      }`}>
                        <div className="flex justify-between">
                          <p className="text-sm font-medium text-gray-800">{iss.detail}</p>
                          <span className="text-xs font-bold">{iss.severity}</span>
                        </div>
                        <p className="text-xs text-gray-500">{iss.category} · {iss.metric}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <RecommendationCard
                recommendation={run.recommendation}
                recommended={run.retraining_recommended}
              />

              <div className="bg-white rounded-xl border border-gray-200 p-5">
                <h3 className="font-semibold text-gray-800 mb-3">Model Versions</h3>
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                    <tr>
                      <th className="px-3 py-2 text-left">Version</th>
                      <th className="px-3 py-2 text-left">Status</th>
                      <th className="px-3 py-2 text-left">Baseline F1</th>
                      <th className="px-3 py-2 text-left">Health</th>
                      <th className="px-3 py-2 text-left">Retrain</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {comparison.map((c) => (
                      <tr key={c.version}>
                        <td className="px-3 py-2 font-medium">{c.version}</td>
                        <td className="px-3 py-2">{c.status}</td>
                        <td className="px-3 py-2">{c.baseline_f1?.toFixed(3) ?? '—'}</td>
                        <td className="px-3 py-2">{c.latest_health_score?.toFixed(0) ?? '—'}</td>
                        <td className="px-3 py-2">{c.retraining_recommended ? '⚠️' : '✓'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {tab === 'drift' && (
            <div className="space-y-4">
              <DriftTable features={run.feature_drift} />
              {run.prediction_drift && (
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                  <h3 className="font-semibold text-gray-800 mb-3">🎯 Prediction Drift</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500 text-xs uppercase mb-2">Previous Distribution</p>
                      {Object.entries(run.prediction_drift.previous_distribution).map(([k, v]) => (
                        <div key={k} className="flex justify-between border-b border-gray-100 py-1">
                          <span>{k}</span>
                          <span className="font-mono">{(v * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <p className="text-gray-500 text-xs uppercase mb-2">Current Distribution</p>
                      {Object.entries(run.prediction_drift.current_distribution).map(([k, v]) => (
                        <div key={k} className="flex justify-between border-b border-gray-100 py-1">
                          <span>{k}</span>
                          <span className="font-mono font-semibold">{(v * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-3">
                    JS divergence: <strong>{run.prediction_drift.js.toFixed(3)}</strong> ({run.prediction_drift.level})
                  </p>
                </div>
              )}
            </div>
          )}

          {tab === 'quality' && <QualityPanel quality={run.data_quality} />}

          {tab === 'performance' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard title="Accuracy" value={run.performance?.accuracy?.toFixed(3) ?? '—'} color="teal" />
                <StatCard title="F1" value={run.performance?.f1?.toFixed(3) ?? '—'} color="blue" />
                <StatCard title="ROC-AUC" value={run.performance?.roc_auc?.toFixed(3) ?? '—'} color="green" />
                <StatCard
                  title="Δ F1"
                  value={run.performance?.delta_f1 !== null && run.performance?.delta_f1 !== undefined
                    ? `${(run.performance.delta_f1 * 100).toFixed(2)}%` : '—'}
                  color={run.performance && run.performance.delta_f1 && run.performance.delta_f1 < -0.03 ? 'red' : 'green'}
                />
              </div>
              <PerformanceChart history={history} />
            </div>
          )}
        </>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
          <p className="text-gray-500 mb-3">No monitoring runs yet for this model.</p>
          <p className="text-sm text-gray-500">Click "Run Monitoring" to start.</p>
        </div>
      )}
    </div>
  );
};

export default ModelDetails;