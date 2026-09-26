from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
import random
import json
from pathlib import Path

from ...core.database import get_db
from ...core.config import settings
from ...models.ml_model import MLModel
from ...models.model_version import ModelVersion
from ...models.monitoring_run import MonitoringRun
from ...models.user import User
from ...schemas.monitoring import (
    MonitoringRunResponse, FeatureDrift, PredictionDriftInfo,
    DataQualityInfo, PerformanceInfo, ComparisonRow,
)
from ...services.data_generator import (
    generate_production_distributions, generate_predictions,
)
from ...services.drift_service import analyze_feature_drift, overall_drift_level
from ...services.quality_service import analyze_quality
from ...services.performance_service import simulate_performance
from ...services.prediction_drift_service import compute_prediction_drift
from ...services.health_service import compute_health_score, classify_health
from ...services.explanation_service import get_top_issues
from ...services.recommendation_service import should_retrain
from ...services.alert_service import generate_alerts
from ...api.dependencies.auth import get_current_user

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


def _run_monitoring(db: Session, model: MLModel, version: ModelVersion, drift_intensity: float, user_id: str):
    # 1. Generate production data
    production = generate_production_distributions(model.domain or "credit", drift_intensity)
    
    # 2. Feature drift
    feature_drift = analyze_feature_drift(version.training_distributions, production)
    overall = overall_drift_level(feature_drift)
    
    # 3. Prediction drift
    prev_preds = version.training_predictions or generate_predictions(500, drift=0.0)
    cur_preds = generate_predictions(500, drift=drift_intensity)
    pd_result = compute_prediction_drift(prev_preds, cur_preds)
    
    # 4. Data quality
    dq = analyze_quality(version.training_distributions, production)
    
    # 5. Performance
    perf = simulate_performance(version, overall)
    
    # 6. Health score
    health = compute_health_score(dq["score"], feature_drift, pd_result, perf)
    status = classify_health(health)
    
    # 7. Top issues + recommendation
    top_issues = get_top_issues(feature_drift, dq, perf)
    retrain_recommended, recommendation = should_retrain(health, feature_drift, perf)
    
    # 8. Persist
    count = db.query(MonitoringRun).count()
    run_ref = f"MW-{10001 + count}"
    run = MonitoringRun(
        run_ref=run_ref,
        model_id=model.id,
        version_id=version.id,
        feature_drift=feature_drift,
        overall_drift_level=overall,
        prediction_drift=pd_result,
        data_quality=dq,
        data_quality_score=dq["score"],
        performance=perf,
        performance_score=perf["score"],
        health_score=health,
        health_status=status,
        top_issues=top_issues,
        recommendation=recommendation,
        retraining_recommended=retrain_recommended,
        created_by=user_id,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    # Update model
    model.current_health = status
    model.current_health_score = str(health)
    db.commit()
    
    # 9. Generate alerts
    generate_alerts(db, model, run, feature_drift, pd_result, dq, perf)
    
    return run


@router.post("/models/{model_id}/run", response_model=MonitoringRunResponse)
def run_monitoring(
    model_id: str,
    drift_intensity: float = 0.3,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    version = (
        db.query(ModelVersion)
        .filter(ModelVersion.model_id == model.id, ModelVersion.status == "production")
        .order_by(desc(ModelVersion.training_date))
        .first()
    )
    if not version:
        raise HTTPException(status_code=400, detail="No production version found")
    
    run = _run_monitoring(db, model, version, drift_intensity, current_user.id)
    return _serialize_run(db, run)


@router.get("/models/{model_id}/latest", response_model=MonitoringRunResponse)
def latest_run(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = (
        db.query(MonitoringRun)
        .filter(MonitoringRun.model_id == model_id)
        .order_by(desc(MonitoringRun.created_at))
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="No monitoring runs yet")
    return _serialize_run(db, run)


@router.get("/runs/{run_id}", response_model=MonitoringRunResponse)
def get_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = db.query(MonitoringRun).filter(MonitoringRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _serialize_run(db, run)


@router.get("/models/{model_id}/history")
def run_history(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    runs = (
        db.query(MonitoringRun)
        .filter(MonitoringRun.model_id == model_id)
        .order_by(desc(MonitoringRun.created_at))
        .limit(30)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "run_ref": r.run_ref,
            "health_score": r.health_score,
            "health_status": r.health_status,
            "overall_drift_level": r.overall_drift_level,
            "retraining_recommended": r.retraining_recommended,
            "created_at": r.created_at.isoformat(),
        } for r in runs
    ]


@router.get("/models/{model_id}/compare", response_model=list[ComparisonRow])
def compare_versions(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    versions = (
        db.query(ModelVersion)
        .filter(ModelVersion.model_id == model_id)
        .order_by(ModelVersion.training_date)
        .all()
    )
    rows = []
    for v in versions:
        last_run = (
            db.query(MonitoringRun)
            .filter(MonitoringRun.version_id == v.id)
            .order_by(desc(MonitoringRun.created_at))
            .first()
        )
        rows.append(ComparisonRow(
            version=v.version,
            status=v.status,
            training_date=v.training_date.isoformat(),
            baseline_f1=v.baseline_f1,
            latest_health_score=last_run.health_score if last_run else None,
            latest_overall_drift=last_run.overall_drift_level if last_run else None,
            retraining_recommended=last_run.retraining_recommended if last_run else None,
        ))
    return rows


def _serialize_run(db: Session, run: MonitoringRun) -> MonitoringRunResponse:
    model = db.query(MLModel).filter(MLModel.id == run.model_id).first()
    version = db.query(ModelVersion).filter(ModelVersion.id == run.version_id).first()
    
    return MonitoringRunResponse(
        id=str(run.id),
        run_ref=run.run_ref,
        model_id=str(run.model_id),
        model_name=model.name if model else "—",
        version=version.version if version else "—",
        feature_drift=[FeatureDrift(**f) for f in run.feature_drift or []],
        overall_drift_level=run.overall_drift_level,
        prediction_drift=PredictionDriftInfo(**run.prediction_drift) if run.prediction_drift else None,
        data_quality=DataQualityInfo(**run.data_quality),
        performance=PerformanceInfo(**run.performance) if run.performance else None,
        health_score=run.health_score,
        health_status=run.health_status,
        top_issues=run.top_issues or [],
        recommendation=run.recommendation,
        retraining_recommended=run.retraining_recommended,
        created_at=run.created_at.isoformat(),
    )