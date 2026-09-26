from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...services.auth_service import authenticate, create_token_for_user
from ...schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token_for_user(user)
    return LoginResponse(
        access_token=token,
        user_id=str(user.id),
        full_name=user.full_name,
    )