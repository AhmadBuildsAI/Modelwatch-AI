import React from 'react';

interface Props {
  score: number;
  status: string;
}

const HealthGauge: React.FC<Props> = ({ score, status }) => {
  const pct = Math.min(100, Math.max(0, Math.round(score)));
  const color =
    status === 'CRITICAL' ? '#dc2626' :
    status === 'WARNING' ? '#f59e0b' : '#16a34a';
  const bg =
    status === 'CRITICAL' ? 'bg-red-50' :
    status === 'WARNING' ? 'bg-yellow-50' : 'bg-green-50';

  const circumference = 2 * Math.PI * 56;
  const dash = (pct / 100) * circumference;

  return (
    <div className={`${bg} rounded-2xl p-6 text-center`}>
      <p className="text-sm font-medium text-gray-500 mb-3">MODEL HEALTH</p>
      <div className="relative inline-flex">
        <svg className="w-40 h-40">
          <circle cx="80" cy="80" r="56" stroke="#e5e7eb" strokeWidth="10" fill="transparent" />
          <circle
            cx="80" cy="80" r="56"
            stroke={color} strokeWidth="10" strokeLinecap="round" fill="transparent"
            strokeDasharray={`${dash} ${circumference}`}
            transform="rotate(-90 80 80)"
            style={{ transition: 'stroke-dasharray 0.6s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold" style={{ color }}>{pct}</span>
          <span className="text-xs text-gray-500">/ 100</span>
        </div>
      </div>
      <p className="mt-3 text-lg font-semibold" style={{ color }}>{status}</p>
    </div>
  );
};

export default HealthGauge;