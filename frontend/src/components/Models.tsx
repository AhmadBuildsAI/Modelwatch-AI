import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import StatCard from './StatCard';
import { listModels } from '../services/monitoring';
import { ModelListItem } from '../types';

const HEALTH_STYLE: Record<string, string> = {
  HEALTHY: 'bg-green-100 text-green-700',
  WARNING: 'bg-yellow-100 text-yellow-700',
  CRITICAL: 'bg-red-100 text-red-700',
};

const Models: React.FC = () => {
  const [models, setModels] = useState<ModelListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listModels()
      .then(setModels)
      .catch(() => toast.error('Failed to load models'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Model Registry</h1>
        <p className="text-gray-500 text-sm">{models.length} models registered</p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : models.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500">
          No models found.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {models.map((m) => (
            <Link
              key={m.id}
              to={`/models/${m.id}`}
              className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-semibold text-gray-800">{m.name}</h3>
                  <p className="text-xs text-gray-500">
                    {m.model_ref} · {m.task_type} {m.domain && `· ${m.domain}`}
                  </p>
                </div>
                {m.current_health && (
                  <span className={`text-xs font-bold px-2 py-1 rounded ${HEALTH_STYLE[m.current_health] || HEALTH_STYLE.HEALTHY}`}>
                    {m.current_health}
                  </span>
                )}
              </div>
              <div className="flex justify-between text-sm text-gray-600 mt-3">
                <span>Version: {m.latest_version || '—'}</span>
                {m.current_health_score !== null && (
                  <span className="font-semibold">Health {m.current_health_score.toFixed(0)}</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Models;