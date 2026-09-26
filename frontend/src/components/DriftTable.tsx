import React from 'react';
import { FeatureDrift } from '../types';

interface Props {
  features: FeatureDrift[];
}

const LEVEL_STYLE: Record<string, string> = {
  HIGH: 'bg-red-100 text-red-700',
  MEDIUM: 'bg-yellow-100 text-yellow-700',
  LOW: 'bg-green-100 text-green-700',
};

const DriftTable: React.FC<Props> = ({ features }) => {
  if (!features || features.length === 0) {
    return <p className="text-sm text-gray-500">No feature drift data.</p>;
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
          <tr>
            <th className="px-4 py-3 text-left">Feature</th>
            <th className="px-4 py-3 text-left">PSI</th>
            <th className="px-4 py-3 text-left">KS p-value</th>
            <th className="px-4 py-3 text-left">JS Divergence</th>
            <th className="px-4 py-3 text-left">Drift Level</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {features.map((f) => (
            <tr key={f.feature} className="hover:bg-gray-50">
              <td className="px-4 py-3 font-medium font-mono text-gray-800">{f.feature}</td>
              <td className="px-4 py-3 text-gray-700">{f.psi.toFixed(3)}</td>
              <td className="px-4 py-3 text-gray-700">{f.ks_pvalue.toFixed(3)}</td>
              <td className="px-4 py-3 text-gray-700">{f.js.toFixed(3)}</td>
              <td className="px-4 py-3">
                <span className={`px-2 py-1 rounded text-xs font-bold ${LEVEL_STYLE[f.level] || LEVEL_STYLE.LOW}`}>
                  {f.level}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DriftTable;