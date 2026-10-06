from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, UserOut
from app.auth import SESSION_COOKIE

router=APIRouter()

@router.post("/login",response_model=UserOut)
def login(data: LoginRequest,response: Response,db: Session=Depends(get_db)):
    user=db.query(User).filter(User.username==data.username).first()
    if not user or user.password!=data.password:
        raise HTTPException(status_code=401,detail="Неверные данные")
    response.set_cookie(SESSION_COOKIE,str(user.id),httponly=True,samesite="lax")
    return user

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE)
    return {"status":"ok"}
