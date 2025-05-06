from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from database import get_db
from models import User

router = APIRouter(prefix="/users", tags=["users"])

api_key_header = APIKeyHeader(name="X-API-Key")

@router.post("")
async def create_user(email: str, username: str, db: Session = Depends(get_db), api_key: str = Depends(api_key_header)):
    if api_key != "admin-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    db_user = User(email=email, username=username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created", "user": {"id": db_user.id, "email": db_user.email, "username": db_user.username}}

@router.get("")
async def get_users(db: Session = Depends(get_db), api_key: str = Depends(api_key_header)):
    if api_key != "admin-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "username": u.username} for u in users]