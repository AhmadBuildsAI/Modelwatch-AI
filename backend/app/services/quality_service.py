"""
Data quality checks on production data.
"""
import numpy as np
from typing import Dict, List
from ..core.config import settings


def analyze_quality(baseline: Dict, production: Dict) -> Dict:
    issues = []
    outlier_rate = 0.0
    dup_rate = max((float(info.get("duplicate_rate", 0.0)) for info in production.values()), default=0.0)
    null_rate = max((float(info.get("null_rate", 0.0)) for info in production.values()), default=0.0)

    if null_rate > settings.NULL_RATE_CRIT:
        issues.append({"type": "null_rate", "feature": "multiple", "severity": "HIGH", "detail": f"Null rate {null_rate*100:.1f}% exceeds critical threshold"})
    elif null_rate > settings.NULL_RATE_WARN:
        issues.append({"type": "null_rate", "feature": "multiple", "severity": "MEDIUM", "detail": f"Null rate {null_rate*100:.1f}% exceeds warning threshold"})
    if dup_rate > 0.05:
        issues.append({"type": "duplicate_rate", "feature": "dataset", "severity": "MEDIUM", "detail": f"Duplicate rate {dup_rate*100:.1f}% is elevated"})
    
    for fname, pinfo in production.items():
        # Missing values (we simulate some nulls during production gen)
        if pinfo.get("type") == "numeric":
            sample = pinfo.get("sample", [])
            if not sample:
                continue
            
            # Range violations
            b = baseline.get(fname, {})
            b_min = b.get("min", 0)
            b_max = b.get("max", 0)
            if b_max > b_min:
                violations = sum(1 for v in sample if v < b_min - (b_max - b_min) * 0.2 or v > b_max + (b_max - b_min) * 0.2)
                viol_rate = violations / len(sample)
                if viol_rate > 0.05:
                    issues.append({
                        "type": "range_violation",
                        "feature": fname,
                        "severity": "MEDIUM",
                        "detail": f"{viol_rate*100:.1f}% of values outside training range",
                    })
            
            # Outliers (3σ)
            mean = b.get("mean", 0)
            std = b.get("std", 1)
            outliers = sum(1 for v in sample if std > 0 and abs(v - mean) > 3 * std)
            outlier_rate = max(outlier_rate, outliers / max(1, len(sample)))
        else:
            # Unexpected categories
            expected = set(baseline.get(fname, {}).get("categories", []))
            actual = set(pinfo.get("categories", []))
            unexpected = actual - expected
            if unexpected:
                issues.append({
                    "type": "unexpected_category",
                    "feature": fname,
                    "severity": "HIGH",
                    "detail": f"Unexpected categories: {list(unexpected)}",
                })
    
    if outlier_rate > settings.OUTLIER_RATE_WARN:
        issues.append({
            "type": "high_outlier_rate",
            "feature": "multiple",
            "severity": "MEDIUM",
            "detail": f"Outlier rate {outlier_rate*100:.1f}% exceeds threshold",
        })
    
    # Compute score
    score = 100.0
    score -= min(40, outlier_rate * 400)
    score -= len([i for i in issues if i["severity"] == "HIGH"]) * 10
    score -= min(15, dup_rate * 100)
    score -= len([i for i in issues if i["severity"] == "MEDIUM"]) * 4
    score = max(0.0, score)
    
    return {
        "null_rate": round(null_rate, 4),
        "outlier_rate": round(outlier_rate, 4),
        "dup_rate": round(dup_rate, 4),
        "issues": issues,
        "score": round(score, 2),
    }