"""
Statistical drift detection per feature.
PSI, KS test, and Jensen-Shannon divergence.
"""
import numpy as np
from scipy.stats import ks_2samp, entropy
from typing import Dict, List
from ..core.config import settings


def compute_psi(baseline_sample: List[float], production_sample: List[float], bins: int = 10) -> float:
    """
    Population Stability Index.
    Uses quantile bins from baseline.
    """
    if not baseline_sample or not production_sample:
        return 0.0
    
    b = np.asarray(baseline_sample, dtype=float)
    p = np.asarray(production_sample, dtype=float)
    
    # Quantile-based bin edges
    breakpoints = np.quantile(b, np.linspace(0, 1, bins + 1))
    breakpoints = np.unique(breakpoints)
    if len(breakpoints) < 2:
        return 0.0
    
    b_hist, _ = np.histogram(b, bins=breakpoints)
    p_hist, _ = np.histogram(p, bins=breakpoints)
    
    b_pct = b_hist / max(1, b_hist.sum())
    p_pct = p_hist / max(1, p_hist.sum())
    
    # Avoid log(0)
    eps = 1e-6
    b_pct = np.where(b_pct == 0, eps, b_pct)
    p_pct = np.where(p_pct == 0, eps, p_pct)
    
    psi = np.sum((p_pct - b_pct) * np.log(p_pct / b_pct))
    return float(psi)


def compute_ks(baseline_sample: List[float], production_sample: List[float]) -> float:
    """KS test p-value"""
    if not baseline_sample or not production_sample:
        return 1.0
    _, p_value = ks_2samp(baseline_sample, production_sample)
    return float(p_value)


def compute_js_numeric(baseline_sample: List[float], production_sample: List[float], bins: int = 20) -> float:
    """Jensen-Shannon divergence for numeric"""
    if not baseline_sample or not production_sample:
        return 0.0
    b = np.asarray(baseline_sample, dtype=float)
    p = np.asarray(production_sample, dtype=float)
    lo = min(b.min(), p.min())
    hi = max(b.max(), p.max())
    if hi <= lo:
        return 0.0
    edges = np.linspace(lo, hi, bins + 1)
    b_hist, _ = np.histogram(b, bins=edges)
    p_hist, _ = np.histogram(p, bins=edges)
    b_pct = b_hist / max(1, b_hist.sum())
    p_pct = p_hist / max(1, p_hist.sum())
    m = 0.5 * (b_pct + p_pct)
    return float(0.5 * entropy(b_pct, m) + 0.5 * entropy(p_pct, m))


def compute_psi_categorical(baseline_freq: Dict, production_freq: Dict) -> float:
    """Population Stability Index for categorical distributions."""
    keys = set(baseline_freq.keys()) | set(production_freq.keys())
    if not keys:
        return 0.0
    eps = 1e-6
    b = np.array([max(float(baseline_freq.get(k, 0.0)), eps) for k in keys], dtype=float)
    p = np.array([max(float(production_freq.get(k, 0.0)), eps) for k in keys], dtype=float)
    b = b / b.sum()
    p = p / p.sum()
    return float(np.sum((p - b) * np.log(p / b)))


def compute_js_categorical(baseline_freq: Dict, production_freq: Dict) -> float:
    """JS divergence for categorical distributions"""
    keys = set(baseline_freq.keys()) | set(production_freq.keys())
    p = np.array([baseline_freq.get(k, 1e-6) for k in keys])
    q = np.array([production_freq.get(k, 1e-6) for k in keys])
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * entropy(p, m) + 0.5 * entropy(q, m))


def classify_drift(psi: float, js: float) -> str:
    """Combine PSI + JS into a single drift level"""
    if psi >= settings.PSI_MEDIUM or js >= settings.JS_MEDIUM:
        return "HIGH"
    if psi >= settings.PSI_LOW or js >= settings.JS_LOW:
        return "MEDIUM"
    return "LOW"


def analyze_feature_drift(baseline: Dict, production: Dict) -> List[Dict]:
    """Compute drift for every feature in baseline"""
    results = []
    for fname, binfo in baseline.items():
        pinfo = production.get(fname)
        if not pinfo:
            continue
        
        if binfo["type"] == "numeric":
            b_sample = binfo.get("sample", [])
            p_sample = pinfo.get("sample", [])
            psi = compute_psi(b_sample, p_sample)
            ks_p = compute_ks(b_sample, p_sample)
            js = compute_js_numeric(b_sample, p_sample)
            results.append({
                "feature": fname,
                "psi": round(psi, 4),
                "ks_pvalue": round(ks_p, 4),
                "js": round(js, 4),
                "level": classify_drift(psi, js),
                "training_mean": round(float(binfo.get("mean", 0)), 2),
                "production_mean": round(float(pinfo.get("mean", 0)), 2),
            })
        else:
            b_freq = binfo.get("frequencies", {})
            p_freq = pinfo.get("frequencies", {})
            js = compute_js_categorical(b_freq, p_freq)
            psi = compute_psi_categorical(b_freq, p_freq)
            ks_p = 1.0  # N/A for categorical
            results.append({
                "feature": fname,
                "psi": round(psi, 4),
                "ks_pvalue": round(ks_p, 4),
                "js": round(js, 4),
                "level": classify_drift(psi, js),
                "training_mean": None,
                "production_mean": None,
            })
    
    results.sort(key=lambda x: x["psi"], reverse=True)
    return results


def overall_drift_level(feature_drift: List[Dict]) -> str:
    if not feature_drift:
        return "LOW"
    high = sum(1 for f in feature_drift if f["level"] == "HIGH")
    medium = sum(1 for f in feature_drift if f["level"] == "MEDIUM")
    if high >= 1:
        return "HIGH"
    if medium >= 1:
        return "MEDIUM"
    return "LOW"