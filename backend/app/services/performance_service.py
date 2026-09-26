"""
Simulate performance monitoring: current vs baseline accuracy/f1/auc.
In a real system, this would use ground-truth labels over time.
"""
import random


def simulate_performance(version, drift_level: str) -> Dict:
    base_acc = version.baseline_accuracy or 0.85
    base_f1 = version.baseline_f1 or 0.82
    base_auc = version.baseline_roc_auc or 0.88
    
    # Degradation proportional to drift level
    factor = {"LOW": 1.0, "MEDIUM": 0.93, "HIGH": 0.85}.get(drift_level, 1.0)
    
    cur_acc = base_acc * factor + random.uniform(-0.01, 0.01)
    cur_f1 = base_f1 * factor + random.uniform(-0.01, 0.01)
    cur_auc = base_auc * factor + random.uniform(-0.01, 0.01)
    
    delta_f1 = cur_f1 - base_f1
    
    # Score: scale F1 drop into [0, 100]
    score = max(0.0, min(100.0, 100.0 + (delta_f1 * 400)))
    
    return {
        "accuracy": round(cur_acc, 4),
        "f1": round(cur_f1, 4),
        "roc_auc": round(cur_auc, 4),
        "previous_f1": round(base_f1, 4),
        "delta_f1": round(delta_f1, 4),
        "score": round(score, 2),
    }