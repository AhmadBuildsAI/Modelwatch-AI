"""
Generate synthetic baseline (training) distributions and current (production) distributions.
Supports controlled drift injection for demo purposes.
"""
import random
import numpy as np
from datetime import date, timedelta
from typing import Dict, List


FEATURE_SCHEMAS = {
    "credit": {
        "task_type": "classification",
        "features": {
            "monthly_income": {"type": "numeric", "mean": 45000, "std": 15000},
            "loan_amount": {"type": "numeric", "mean": 250000, "std": 90000},
            "employment_years": {"type": "numeric", "mean": 4.2, "std": 2.1},
            "credit_score": {"type": "numeric", "mean": 680, "std": 55},
            "previous_defaults": {"type": "categorical", "categories": [0, 1, 2, 3]},
        },
    },
    "churn": {
        "task_type": "classification",
        "features": {
            "tenure_months": {"type": "numeric", "mean": 18.5, "std": 8.0},
            "monthly_charges": {"type": "numeric", "mean": 65.0, "std": 22.0},
            "total_charges": {"type": "numeric", "mean": 1500.0, "std": 800.0},
            "contract_type": {"type": "categorical", "categories": ["monthly", "1yr", "2yr"]},
        },
    },
    "fraud": {
        "task_type": "classification",
        "features": {
            "transaction_amount": {"type": "numeric", "mean": 120.0, "std": 80.0},
            "hour_of_day": {"type": "numeric", "mean": 14.0, "std": 5.0},
            "merchant_category": {"type": "categorical", "categories": ["retail", "food", "online", "travel"]},
            "distance_from_home": {"type": "numeric", "mean": 12.0, "std": 20.0},
        },
    },
}


def _summarize_numeric(values: np.ndarray) -> Dict:
    """Store quantile summary for drift computation"""
    qs = np.quantile(values, [0.05, 0.25, 0.5, 0.75, 0.95]).tolist()
    return {
        "type": "numeric",
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
        "quantiles": [float(q) for q in qs],
        "sample": values[:200].tolist(),  # sample for KS test
        "null_rate": 0.0,
        "duplicate_rate": 0.0,
    }


def _summarize_categorical(values: List) -> Dict:
    from collections import Counter
    counts = Counter(values)
    total = sum(counts.values())
    return {
        "type": "categorical",
        "categories": list(counts.keys()),
        "frequencies": {k: v / total for k, v in counts.items()},
        "sample": values[:200],
        "null_rate": 0.0,
        "duplicate_rate": 0.0,
    }


def generate_training_distributions(domain: str, n: int = 2000) -> Dict:
    spec = FEATURE_SCHEMAS.get(domain, FEATURE_SCHEMAS["credit"])
    out = {}
    for fname, fs in spec["features"].items():
        if fs["type"] == "numeric":
            vals = np.random.normal(fs["mean"], fs["std"], n)
            out[fname] = _summarize_numeric(vals)
        else:
            cats = fs["categories"]
            vals = np.random.choice(cats, n).tolist()
            out[fname] = _summarize_categorical(vals)
    return out


def generate_production_distributions(domain: str, drift_intensity: float = 0.3, n: int = 500) -> Dict:
    """drift_intensity: 0.0 = no drift, 1.0 = severe drift"""
    spec = FEATURE_SCHEMAS.get(domain, FEATURE_SCHEMAS["credit"])
    out = {}
    for fname, fs in spec["features"].items():
        if fs["type"] == "numeric":
            # Shift mean and/or increase std proportional to drift_intensity
            mean_shift = fs["std"] * 1.5 * drift_intensity * random.choice([-1, 1])
            std_scale = 1.0 + drift_intensity * 0.5
            vals = np.random.normal(fs["mean"] + mean_shift, fs["std"] * std_scale, n)
            summary = _summarize_numeric(vals)
            summary["null_rate"] = float(min(0.12, drift_intensity * 0.08 if drift_intensity > 0.65 else 0.0))
            summary["duplicate_rate"] = float(min(0.10, drift_intensity * 0.05 if drift_intensity > 0.75 else 0.0))
            out[fname] = summary
        else:
            # Randomly vary category weights
            cats = fs["categories"]
            weights = np.ones(len(cats))
            if drift_intensity > 0.2:
                weights = np.random.dirichlet(np.ones(len(cats)) * (1.0 + drift_intensity * 3))
            vals = np.random.choice(cats, n, p=weights / weights.sum()).tolist()
            summary = _summarize_categorical(vals)
            summary["null_rate"] = float(min(0.12, drift_intensity * 0.08 if drift_intensity > 0.65 else 0.0))
            summary["duplicate_rate"] = float(min(0.10, drift_intensity * 0.05 if drift_intensity > 0.75 else 0.0))
            out[fname] = summary
    return out


def generate_predictions(n: int, drift: float = 0.0) -> Dict[str, float]:
    """Class distribution over predictions"""
    base = np.array([0.62, 0.28, 0.10])  # low, medium, high
    if drift > 0:
        # Push more to high-risk
        shift = np.array([-drift * 0.3, drift * 0.05, drift * 0.25])
        base = np.clip(base + shift, 0.01, 1.0)
        base = base / base.sum()
    return {"low": float(base[0]), "medium": float(base[1]), "high": float(base[2])}


DEFAULT_MODELS = [
    {"name": "CreditShield Default Model", "domain": "credit", "task_type": "classification"},
    {"name": "ChurnShield Retention Model", "domain": "churn", "task_type": "classification"},
    {"name": "FraudGuard Transaction Model", "domain": "fraud", "task_type": "classification"},
]


def get_feature_schema(domain: str) -> Dict:
    spec = FEATURE_SCHEMAS.get(domain, FEATURE_SCHEMAS["credit"])
    return {
        fname: {
            "type": fs["type"],
            **({"mean": fs["mean"], "std": fs["std"]} if fs["type"] == "numeric" else {"categories": fs["categories"]}),
        }
        for fname, fs in spec["features"].items()
    }