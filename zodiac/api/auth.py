from datetime import UTC, datetime, timedelta
from typing import Optional

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr

from zodiac.config import JWT_ALGORITHM, JWT_SECRET_KEY
from zodiac.entities.db.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    token_type: str = "bearer"

async def authenticate_user(email: str, password: str) -> Optional[User]:
    user = await User.find_one(User.email == email)
    if user and bcrypt.verify(password, user.password):
        return user
    return None

def create_access_token(user_id: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode = {"exp": expire, "sub": user_id}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = await User.get(user_id)
    if user is None:
        raise credentials_exception
    return user
