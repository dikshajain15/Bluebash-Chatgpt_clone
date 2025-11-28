# app/services/auth_service.py
from sqlalchemy.orm import Session
from app.models.models import User
from app.utils.security import hash_password, verify_password, create_access_token
from typing import Optional

def create_user(db: Session, username: str, password: str) -> User:
    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_token_for_user(user: User):
    data = {"user_id": user.id, "username": user.username}
    token = create_access_token(data)
    return token
