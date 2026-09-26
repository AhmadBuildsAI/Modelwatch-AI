from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, timedelta
import random
from .core.config import settings
from .core.database import engine, Base, SessionLocal
from .core.security import hash_password
from .core.logging_config import setup_logging
from .api.routes import auth, models, monitoring, alerts, analytics

logger = setup_logging()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(models.router, prefix=settings.API_V1_STR)
app.include_router(monitoring.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)


@app.get("/health")
def health():
    return {"status": "healthy", "version": settings.VERSION}


@app.on_event("startup")
def startup():
    from .models.user import User
    from .models.ml_model import MLModel
    from .models.model_version import ModelVersion
    from .services.data_generator import (
        DEFAULT_MODELS, get_feature_schema,
        generate_training_distributions, generate_predictions,
    )
    
    db = SessionLocal()
    try:
        # Admin user
        admin = None
        if db.query(User).count() == 0:
            admin = User(
                email="admin@modelwatch.com",
                password_hash=hash_password("admin123"),
                full_name="Admin User",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            logger.info("Created admin user")
        else:
            admin = db.query(User).first()
        
        # Seed models
        if db.query(MLModel).count() == 0:
            for i, spec in enumerate(DEFAULT_MODELS):
                model_ref = f"MDL-{100 + i:03d}"
                m = MLModel(
                    model_ref=model_ref,
                    name=spec["name"],
                    description=f"Synthetic {spec['domain']} model for demo",
                    task_type=spec["task_type"],
                    domain=spec["domain"],
                    feature_schema=get_feature_schema(spec["domain"]),
                    created_by=admin.id,
                )
                db.add(m)
                db.commit()
                db.refresh(m)
                
                # Version 1.0 (production)
                training_dists = generate_training_distributions(spec["domain"])
                v1 = ModelVersion(
                    model_id=m.id,
                    version="v1.0",
                    status="production",
                    training_date=date.today() - timedelta(days=90),
                    dataset_version="ds-2026-Q2",
                    baseline_accuracy=0.86,
                    baseline_f1=0.83,
                    baseline_roc_auc=0.89,
                    training_distributions=training_dists,
                    training_predictions=generate_predictions(500, drift=0.0),
                )
                db.add(v1)
                
                # Version 1.1 (testing)
                v2 = ModelVersion(
                    model_id=m.id,
                    version="v1.1",
                    status="testing",
                    training_date=date.today() - timedelta(days=30),
                    dataset_version="ds-2026-Q3",
                    baseline_accuracy=0.88,
                    baseline_f1=0.85,
                    baseline_roc_auc=0.91,
                    training_distributions=training_dists,
                    training_predictions=generate_predictions(500, drift=0.0),
                )
                db.add(v2)
                
                # Version 1.2 (archived)
                v3 = ModelVersion(
                    model_id=m.id,
                    version="v1.2",
                    status="archived",
                    training_date=date.today() - timedelta(days=180),
                    dataset_version="ds-2026-Q1",
                    baseline_accuracy=0.82,
                    baseline_f1=0.79,
                    baseline_roc_auc=0.85,
                    training_distributions=training_dists,
                    training_predictions=generate_predictions(500, drift=0.0),
                )
                db.add(v3)
                db.commit()
            logger.info("Seeded 3 models with 3 versions each")
    finally:
        db.close()