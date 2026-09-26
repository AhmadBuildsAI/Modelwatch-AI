from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ...core.database import get_db
from ...models.ml_model import MLModel
from ...models.monitoring_run import MonitoringRun
from ...models.alert import Alert
from ...models.user import User
from ...api.dependencies.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    models = db.query(MLModel).filter(MLModel.is_active == True).all()
    total = len(models)
    healthy = sum(1 for m in models if m.current_health == "HEALTHY")
    warning = sum(1 for m in models if m.current_health == "WARNING")
    critical = sum(1 for m in models if m.current_health == "CRITICAL")
    unscored = total - healthy - warning - critical
    
    active_alerts = db.query(Alert).filter(Alert.is_acknowledged == False).count()
    critical_alerts = db.query(Alert).filter(
        Alert.is_acknowledged == False, Alert.severity == "CRITICAL"
    ).count()
    
    recent_alerts = (
        db.query(Alert).order_by(desc(Alert.created_at)).limit(5).all()
    )
    
    # Health over time (avg across latest 10 runs)
    runs = db.query(MonitoringRun).order_by(desc(MonitoringRun.created_at)).limit(20).all()
    health_trend = [
        {
            "run_ref": r.run_ref,
            "health_score": r.health_score,
            "created_at": r.created_at.isoformat(),
        } for r in reversed(runs)
    ]
    
    return {
        "total_models": total,
        "healthy": healthy,
        "warning": warning,
        "critical": critical,
        "unscored": unscored,
        "active_alerts": active_alerts,
        "critical_alerts": critical_alerts,
        "recent_alerts": [
            {
                "id": str(a.id),
                "model_name": next((m.name for m in models if str(m.id) == str(a.model_id)), "—"),
                "severity": a.severity,
                "category": a.category,
                "title": a.title,
                "created_at": a.created_at.isoformat(),
            } for a in recent_alerts
        ],
        "health_trend": health_trend,
    }