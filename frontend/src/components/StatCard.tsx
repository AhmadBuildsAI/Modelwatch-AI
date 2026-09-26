import React from 'react';

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  color?: 'teal' | 'green' | 'yellow' | 'red' | 'blue' | 'slate';
  icon?: string;
}

const StatCard: React.FC<Props> = ({ title, value, subtitle, color = 'teal', icon }) => {
  const colors = {
    teal: 'bg-teal-50 border-teal-200 text-teal-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    slate: 'bg-slate-50 border-slate-200 text-slate-700',
  };
  return (
    <div className={`rounded-xl border p-5 ${colors[color]}`}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium opacity-80">{title}</p>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
      <p className="text-3xl font-bold mt-2">{value}</p>
      {subtitle && <p className="text-xs mt-1 opacity-70">{subtitle}</p>}
    </div>
  );
};

export default StatCard;