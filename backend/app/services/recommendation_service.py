"""
Retraining recommendation based on monitoring results.
"""
from typing import Dict, List


def should_retrain(health_score: float, feature_drift: List[Dict], performance: Dict | None) -> tuple:
    reasons = []
    high_drift = [f for f in feature_drift if f["level"] == "HIGH"]
    medium_drift = [f for f in feature_drift if f["level"] == "MEDIUM"]
    
    if len(high_drift) >= 1:
        reasons.append(f"High feature drift on: {', '.join(f['feature'] for f in high_drift[:3])}")
    if len(medium_drift) >= 2:
        reasons.append(f"Multiple features with medium drift ({len(medium_drift)})")
    
    if performance and performance.get("delta_f1") is not None:
        delta = performance["delta_f1"]
        if delta < -0.05:
            reasons.append(f"F1 score dropped by {abs(delta)*100:.1f}%")
    
    if health_score < 60:
        reasons.append(f"Overall health score is critical ({health_score:.0f})")
    
    recommended = len(reasons) >= 1
    
    if recommended:
        message = (
            "⚠ Retraining Recommended\n\n"
            "Reasons:\n"
            + "\n".join(f"• {r}" for r in reasons)
            + "\n\nSuggested action: Train a new model using the latest 30 days "
              "of validated production data and compare against the current version "
              "using the same evaluation harness."
        )
    else:
        message = (
            "✅ No retraining needed at this time.\n\n"
            "Model is performing within expected parameters."
        )
    
    return recommended, message