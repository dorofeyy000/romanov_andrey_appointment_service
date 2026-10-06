from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

SESSION_COOKIE="session_user_id"

def get_current_user(request: Request,db: Session=Depends(get_db)):
    user_id=request.cookies.get(SESSION_COOKIE)
    if not user_id or not user_id.isdigit():
        raise HTTPException(status_code=401,detail="Требуется авторизация")
    user=db.get(User,int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401,detail="Требуется авторизация")
    return user
