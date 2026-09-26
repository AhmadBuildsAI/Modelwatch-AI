from sqlalchemy.orm import Session
from ..models.user import User
from ..core.security import verify_password, create_access_token

def authenticate(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def create_token_for_user(user: User) -> str:
    return create_access_token({"sub": str(user.id), "email": user.email})