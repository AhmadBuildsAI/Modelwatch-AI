from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_models.id"), nullable=False, index=True)
    monitoring_run_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_runs.id"), nullable=True)
    
    severity = Column(String(20), nullable=False)  # CRITICAL | WARNING | INFO
    category = Column(String(50), nullable=False)  # data_drift | prediction_drift | performance | data_quality
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSONB, nullable=True)
    
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)