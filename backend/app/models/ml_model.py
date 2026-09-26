from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_ref = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)
    task_type = Column(String(30), nullable=False)  # classification | regression
    domain = Column(String(80), nullable=True)      # credit | churn | fraud | demand
    
    feature_schema = Column(JSONB, nullable=False)  # {name: {type, range/min/max, categories}}
    current_health = Column(String(20), nullable=True)  # HEALTHY | WARNING | CRITICAL
    current_health_score = Column(String(10), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())