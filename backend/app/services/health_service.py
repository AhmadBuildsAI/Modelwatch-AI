"""
Composite Model Health Score.
"""
from ..core.config import settings


def compute_health_score(
    data_quality_score: float,
    feature_drift: list,
    prediction_drift: dict | None,
    performance: dict | None,
) -> float:
    # Drift penalty: HIGH per feature counts more
    high = sum(1 for f in feature_drift if f["level"] == "HIGH")
    medium = sum(1 for f in feature_drift if f["level"] == "MEDIUM")
    drift_penalty = min(100.0, high * 25.0 + medium * 10.0)
    drift_score = max(0.0, 100.0 - drift_penalty)
    
    # Prediction drift score
    if prediction_drift:
        pd_js = prediction_drift.get("js", 0.0)
        pd_score = max(0.0, 100.0 - pd_js * 250.0)
    else:
        pd_score = 100.0
    
    # Performance score
    perf_score = performance.get("score", 100.0) if performance else 100.0
    
    # Composite
    health = (
        0.25 * data_quality_score
        + 0.30 * drift_score
        + 0.15 * pd_score
        + 0.30 * perf_score
    )
    return round(health, 2)


def classify_health(score: float) -> str:
    if score >= settings.HEALTH_WARN:
        return "HEALTHY"
    if score >= settings.HEALTH_CRIT:
        return "WARNING"
    return "CRITICAL"