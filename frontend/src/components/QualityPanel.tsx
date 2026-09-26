import React from 'react';
import { DataQualityInfo } from '../types';

interface Props {
  quality: DataQualityInfo;
}

const SEV_STYLE: Record<string, string> = {
  HIGH: 'bg-red-50 border-red-200 text-red-700',
  MEDIUM: 'bg-yellow-50 border-yellow-200 text-yellow-700',
  LOW: 'bg-blue-50 border-blue-200 text-blue-700',
};

const QualityPanel: React.FC<Props> = ({ quality }) => (
  <div className="bg-white rounded-xl border border-gray-200 p-5">
    <h3 className="font-semibold text-gray-800 mb-3">🧹 Data Quality</h3>
    <div className="grid grid-cols-3 gap-3 mb-4 text-sm">
      <div>
        <p className="text-gray-500 text-xs">Null Rate</p>
        <p className="font-semibold">{(quality.null_rate * 100).toFixed(2)}%</p>
      </div>
      <div>
        <p className="text-gray-500 text-xs">Outlier Rate</p>
        <p className="font-semibold">{(quality.outlier_rate * 100).toFixed(2)}%</p>
      </div>
      <div>
        <p className="text-gray-500 text-xs">Quality Score</p>
        <p className="font-semibold text-teal-700">{quality.score.toFixed(0)}</p>
      </div>
    </div>

    {quality.issues.length === 0 ? (
      <p className="text-sm text-green-600">✅ No data quality issues detected</p>
    ) : (
      <div className="space-y-2">
        {quality.issues.map((issue, i) => (
          <div key={i} className={`border rounded-lg p-3 text-xs ${SEV_STYLE[issue.severity] || SEV_STYLE.LOW}`}>
            <p className="font-medium">{issue.type.replace(/_/g, ' ')} — {issue.feature}</p>
            <p className="mt-0.5">{issue.detail}</p>
          </div>
        ))}
      </div>
    )}
  </div>
);

export default QualityPanel;