import React from 'react';

interface Props {
  recommendation: string | null;
  recommended: boolean;
}

const RecommendationCard: React.FC<Props> = ({ recommendation, recommended }) => {
  if (!recommendation) return null;
  return (
    <div className={`rounded-xl border p-5 ${recommended ? 'bg-amber-50 border-amber-200' : 'bg-green-50 border-green-200'}`}>
      <h3 className={`font-semibold mb-2 ${recommended ? 'text-amber-800' : 'text-green-800'}`}>
        {recommended ? '⚠️ Retraining Recommended' : '✅ No Retraining Needed'}
      </h3>
      <pre className="text-sm whitespace-pre-wrap text-gray-800 font-sans">
        {recommendation}
      </pre>
    </div>
  );
};

export default RecommendationCard;