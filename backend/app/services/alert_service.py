"""
Alert generation for drift / performance / quality events.
"""
from sqlalchemy.orm import Session
from ..models.alert import Alert


def generate_alerts(
    db: Session,
    model,
    monitoring_run,
    feature_drift,
    prediction_drift,
    data_quality,
    performance,
):
    alerts_created = []
    
    # Data drift alert
    high_drift = [f for f in feature_drift if f["level"] == "HIGH"]
    if high_drift:
        a = Alert(
            model_id=model.id,
            monitoring_run_id=monitoring_run.id,
            severity="CRITICAL" if len(high_drift) >= 2 else "WARNING",
            category="data_drift",
            title=f"High feature drift on {model.name}",
            message=f"{len(high_drift)} feature(s) show HIGH drift: "
                    + ", ".join(f["feature"] for f in high_drift[:3]),
            details={"features": [f["feature"] for f in high_drift]},
        )
        db.add(a)
        alerts_created.append(a)
    
    # Prediction drift
    if prediction_drift and prediction_drift.get("level") == "HIGH":
        a = Alert(
            model_id=model.id,
            monitoring_run_id=monitoring_run.id,
            severity="WARNING",
            category="prediction_drift",
            title=f"Prediction distribution shifted on {model.name}",
            message=f"JS divergence = {prediction_drift['js']:.2f}. "
                    f"Predictions are drifting from baseline.",
            details=prediction_drift,
        )
        db.add(a)
        alerts_created.append(a)
    
    # Performance decay
    if performance and performance.get("delta_f1") is not None and performance["delta_f1"] < -0.05:
        a = Alert(
            model_id=model.id,
            monitoring_run_id=monitoring_run.id,
            severity="CRITICAL" if performance["delta_f1"] < -0.1 else "WARNING",
            category="performance",
            title=f"Performance decline on {model.name}",
            message=f"F1 dropped by {abs(performance['delta_f1'])*100:.1f}% vs baseline.",
            details=performance,
        )
        db.add(a)
        alerts_created.append(a)
    
    # Data quality
    dq_issues = data_quality.get("issues", [])
    high_dq = [i for i in dq_issues if i.get("severity") == "HIGH"]
    if high_dq:
        a = Alert(
            model_id=model.id,
            monitoring_run_id=monitoring_run.id,
            severity="WARNING",
            category="data_quality",
            title=f"Data quality issues on {model.name}",
            message=f"{len(high_dq)} high-severity issue(s) detected in production data.",
            details={"issues": high_dq},
        )
        db.add(a)
        alerts_created.append(a)
    
    db.commit()
    return alerts_created