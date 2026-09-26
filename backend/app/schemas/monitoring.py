from pydantic import BaseModel
from typing import Dict, List, Optional

class ModelListItem(BaseModel):
    id: str
    model_ref: str
    name: str
    task_type: str
    domain: Optional[str]
    current_health: Optional[str]
    current_health_score: Optional[float]
    latest_version: Optional[str]

class VersionInfo(BaseModel):
    id: str
    version: str
    status: str
    training_date: str
    baseline_accuracy: Optional[float]
    baseline_f1: Optional[float]
    baseline_roc_auc: Optional[float]

class FeatureDrift(BaseModel):
    feature: str
    psi: float
    ks_pvalue: float
    js: float
    level: str
    training_mean: Optional[float] = None
    production_mean: Optional[float] = None

class PredictionDriftInfo(BaseModel):
    js: float
    level: str
    previous_distribution: Dict[str, float]
    current_distribution: Dict[str, float]

class DataQualityInfo(BaseModel):
    null_rate: float
    outlier_rate: float
    dup_rate: float
    issues: List[dict]
    score: float

class PerformanceInfo(BaseModel):
    accuracy: Optional[float]
    f1: Optional[float]
    roc_auc: Optional[float]
    previous_f1: Optional[float]
    delta_f1: Optional[float]

class MonitoringRunResponse(BaseModel):
    id: str
    run_ref: str
    model_id: str
    model_name: str
    version: str
    feature_drift: List[FeatureDrift]
    overall_drift_level: str
    prediction_drift: Optional[PredictionDriftInfo]
    data_quality: DataQualityInfo
    performance: Optional[PerformanceInfo]
    health_score: float
    health_status: str
    top_issues: List[dict]
    recommendation: Optional[str]
    retraining_recommended: bool
    created_at: str

class AlertItem(BaseModel):
    id: str
    model_id: str
    model_name: str
    severity: str
    category: str
    title: str
    message: str
    is_acknowledged: bool
    created_at: str

class ComparisonRow(BaseModel):
    version: str
    status: str
    training_date: str
    baseline_f1: Optional[float]
    latest_health_score: Optional[float]
    latest_overall_drift: Optional[str]
    retraining_recommended: Optional[bool]