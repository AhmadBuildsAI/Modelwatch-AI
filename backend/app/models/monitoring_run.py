from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class MonitoringRun(Base):
    __tablename__ = "monitoring_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_ref = Column(String(20), unique=True, nullable=False, index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_models.id"), nullable=False, index=True)
    version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False)
    
    # Drift results
    feature_drift = Column(JSONB, nullable=False)  # [{feature, psi, ks_pvalue, js, level}]
    overall_drift_level = Column(String(20), nullable=False)
    
    # Prediction drift
    prediction_drift = Column(JSONB, nullable=True)  # {js, level, prev_distribution, current_distribution}
    
    # Data quality
    data_quality = Column(JSONB, nullable=False)  # {null_rate, outlier_rate, dup_rate, issues: []}
    data_quality_score = Column(Float, nullable=False)
    
    # Performance
    performance = Column(JSONB, nullable=True)  # {accuracy, f1, roc_auc, previous, delta}
    performance_score = Column(Float, nullable=True)
    
    # Composite
    health_score = Column(Float, nullable=False)
    health_status = Column(String(20), nullable=False)
    
    top_issues = Column(JSONB, nullable=True)  # [{feature, metric, value, severity}]
    recommendation = Column(Text, nullable=True)
    retraining_recommended = Column(Boolean, default=False)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)