from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_models.id"), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="testing")  # production | testing | archived
    
    training_date = Column(Date, nullable=False)
    dataset_version = Column(String(50), nullable=True)
    
    baseline_accuracy = Column(Float, nullable=True)
    baseline_f1 = Column(Float, nullable=True)
    baseline_roc_auc = Column(Float, nullable=True)
    
    # Distribution summaries (means, stds, histograms) for training data
    training_distributions = Column(JSONB, nullable=False)
    training_predictions = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())