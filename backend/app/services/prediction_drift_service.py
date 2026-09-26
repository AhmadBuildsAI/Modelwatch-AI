"""
Prediction drift detection: compare previous vs current prediction distribution.
"""
import numpy as np
from scipy.stats import entropy
from typing import Dict
from ..core.config import settings
from .data_generator import generate_predictions


def compute_prediction_drift(prev_dist: Dict[str, float], cur_dist: Dict[str, float]) -> Dict:
    keys = sorted(set(prev_dist.keys()) | set(cur_dist.keys()))
    p = np.array([prev_dist.get(k, 0.0) for k in keys])
    q = np.array([cur_dist.get(k, 0.0) for k in keys])
    p = p / max(p.sum(), 1e-9)
    q = q / max(q.sum(), 1e-9)
    m = 0.5 * (p + q)
    js = 0.5 * entropy(p, m) + 0.5 * entropy(q, m)
    
    if js >= settings.JS_MEDIUM:
        level = "HIGH"
    elif js >= settings.JS_LOW:
        level = "MEDIUM"
    else:
        level = "LOW"
    
    return {
        "js": round(float(js), 4),
        "level": level,
        "previous_distribution": prev_dist,
        "current_distribution": cur_dist,
    }