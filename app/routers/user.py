from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.database import SessionLocal
import bcrypt
from app.auth import create_access_token, authenticate_user
from datetime import timedelta
from app.utils import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/register")
async def register_user(user: User, db: AsyncSession = Depends(SessionLocal)):
    hashed_password = bcrypt.hashpw(user.hashed_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(username=user.username, hashed_password=hashed_password, telegram_id=user.telegram_id)
    db.add(new_user)
    await db.commit()
    return {"msg": "User created"}


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(SessionLocal)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
