import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { listAlerts, acknowledgeAlert } from '../services/monitoring';
import { AlertItem } from '../types';

const SEV_STYLE: Record<string, string> = {
  CRITICAL: 'bg-red-50 border-red-200',
  WARNING: 'bg-yellow-50 border-yellow-200',
  INFO: 'bg-blue-50 border-blue-200',
};

const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = () => {
    setLoading(true);
    listAlerts().then(setAlerts).catch(() => toast.error('Failed to load alerts')).finally(() => setLoading(false));
  };

  useEffect(() => { refresh(); }, []);

  const handleAck = async (id: string) => {
    try {
      await acknowledgeAlert(id);
      toast.success('Alert acknowledged');
      refresh();
    } catch {
      toast.error('Failed to acknowledge');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Alerts</h1>
        <p className="text-gray-500 text-sm">
          {alerts.length} alerts ({alerts.filter((a) => !a.is_acknowledged).length} unacknowledged)
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : alerts.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
          <p className="text-sm text-gray-500">No alerts. All models healthy 🎉</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((a) => (
            <div key={a.id} className={`rounded-xl border p-5 ${SEV_STYLE[a.severity] || SEV_STYLE.INFO}`}>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                      a.severity === 'CRITICAL' ? 'bg-red-600 text-white' :
                      a.severity === 'WARNING' ? 'bg-yellow-500 text-white' :
                      'bg-blue-500 text-white'
                    }`}>{a.severity}</span>
                    <span className="text-xs text-gray-500">
                      {a.model_name} · {a.category}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-800">{a.title}</h3>
                  <p className="text-sm text-gray-700 mt-1">{a.message}</p>
                </div>
                <div className="flex flex-col items-end gap-2 ml-4">
                  <span className="text-xs text-gray-500">
                    {new Date(a.created_at).toLocaleString()}
                  </span>
                  {!a.is_acknowledged ? (
                    <button
                      onClick={() => handleAck(a.id)}
                      className="px-3 py-1 text-xs bg-white border border-gray-300 rounded hover:bg-gray-50"
                    >
                      Acknowledge
                    </button>
                  ) : (
                    <span className="text-xs text-green-700">✓ Acknowledged</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Alerts;