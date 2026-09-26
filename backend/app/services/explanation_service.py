"""
Identify top issues and produce human-readable explanations.
"""
from typing import List, Dict


def get_top_issues(feature_drift: List[Dict], data_quality: Dict, performance: Dict | None) -> List[Dict]:
    issues = []
    
    # Feature drift
    for f in feature_drift[:5]:
        if f["level"] in ("HIGH", "MEDIUM"):
            issues.append({
                "category": "data_drift",
                "feature": f["feature"],
                "metric": "PSI",
                "value": f["psi"],
                "severity": f["level"],
                "detail": f"{f['feature']} — PSI {f['psi']:.2f} ({f['level']})",
            })
    
    # Data quality issues
    for issue in data_quality.get("issues", [])[:3]:
        issues.append({
            "category": "data_quality",
            "feature": issue.get("feature"),
            "metric": issue.get("type"),
            "value": None,
            "severity": issue.get("severity", "MEDIUM"),
            "detail": issue.get("detail"),
        })
    
    # Performance
    if performance and performance.get("delta_f1") is not None:
        delta = performance["delta_f1"]
        if delta < -0.03:
            issues.append({
                "category": "performance",
                "feature": "model",
                "metric": "F1 change",
                "value": delta,
                "severity": "HIGH" if delta < -0.08 else "MEDIUM",
                "detail": f"F1 dropped by {abs(delta)*100:.1f}% vs baseline",
            })
    
    # Sort by severity
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    issues.sort(key=lambda x: order.get(x["severity"], 3))
    return issues[:8]