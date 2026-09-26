from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ...core.database import get_db
from ...models.ml_model import MLModel
from ...models.model_version import ModelVersion
from ...models.monitoring_run import MonitoringRun
from ...models.user import User
from ...schemas.monitoring import ModelListItem, VersionInfo
from ...api.dependencies.auth import get_current_user

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/", response_model=list[ModelListItem])
def list_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    models = db.query(MLModel).filter(MLModel.is_active == True).all()
    out = []
    for m in models:
        latest = (
            db.query(ModelVersion)
            .filter(ModelVersion.model_id == m.id, ModelVersion.status == "production")
            .order_by(desc(ModelVersion.training_date))
            .first()
        )
        out.append(ModelListItem(
            id=str(m.id),
            model_ref=m.model_ref,
            name=m.name,
            task_type=m.task_type,
            domain=m.domain,
            current_health=m.current_health,
            current_health_score=float(m.current_health_score) if m.current_health_score else None,
            latest_version=latest.version if latest else None,
        ))
    return out


@router.get("/{model_id}")
def get_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Model not found")
    
    versions = db.query(ModelVersion).filter(ModelVersion.model_id == m.id).all()
    latest_run = (
        db.query(MonitoringRun)
        .filter(MonitoringRun.model_id == m.id)
        .order_by(desc(MonitoringRun.created_at))
        .first()
    )
    
    return {
        "id": str(m.id),
        "model_ref": m.model_ref,
        "name": m.name,
        "description": m.description,
        "task_type": m.task_type,
        "domain": m.domain,
        "current_health": m.current_health,
        "current_health_score": float(m.current_health_score) if m.current_health_score else None,
        "feature_schema": m.feature_schema,
        "versions": [
            VersionInfo(
                id=str(v.id),
                version=v.version,
                status=v.status,
                training_date=v.training_date.isoformat(),
                baseline_accuracy=v.baseline_accuracy,
                baseline_f1=v.baseline_f1,
                baseline_roc_auc=v.baseline_roc_auc,
            ) for v in versions
        ],
        "latest_run_id": str(latest_run.id) if latest_run else None,
    }