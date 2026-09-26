from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ...core.database import get_db
from ...models.alert import Alert
from ...models.ml_model import MLModel
from ...models.user import User
from ...schemas.monitoring import AlertItem
from ...api.dependencies.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertItem])
def list_alerts(
    acknowledged: bool | None = None,
    severity: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Alert)
    if acknowledged is not None:
        q = q.filter(Alert.is_acknowledged == acknowledged)
    if severity:
        q = q.filter(Alert.severity == severity)
    rows = q.order_by(desc(Alert.created_at)).limit(100).all()
    
    out = []
    for a in rows:
        m = db.query(MLModel).filter(MLModel.id == a.model_id).first()
        out.append(AlertItem(
            id=str(a.id),
            model_id=str(a.model_id),
            model_name=m.name if m else "—",
            severity=a.severity,
            category=a.category,
            title=a.title,
            message=a.message,
            is_acknowledged=a.is_acknowledged,
            created_at=a.created_at.isoformat(),
        ))
    return out


@router.post("/{alert_id}/acknowledge", response_model=AlertItem)
def acknowledge(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    a.is_acknowledged = True
    db.commit()
    m = db.query(MLModel).filter(MLModel.id == a.model_id).first()
    return AlertItem(
        id=str(a.id),
        model_id=str(a.model_id),
        model_name=m.name if m else "—",
        severity=a.severity,
        category=a.category,
        title=a.title,
        message=a.message,
        is_acknowledged=a.is_acknowledged,
        created_at=a.created_at.isoformat(),
    )