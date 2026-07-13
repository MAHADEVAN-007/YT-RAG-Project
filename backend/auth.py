from datetime import UTC, datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from typing import Annotated
from backend.config import settings
from Databases.UserDB.database import get_db
from Models.models import User

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Models.models import User

import hashlib, secrets

from fastapi import Depends, HTTPException, status

password_hash = PasswordHash.recommended()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Hashing the password ->
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# Takes the password and hashed password, and verifies both of them ->
def  verify_hash_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

def hash_reset_token(token) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

# Creating access_token ->
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )
    return encoded_jwt

def verify_access_tokens(token: str) -> str | None:
    try: payload = jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=[settings.algorithm],
        options={'require': ['exp', 'sub']},
    )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get('sub')
    
async def get_current_user(token: Annotated[str, Depends(oauth2_schema)], db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    user_id = verify_access_tokens(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid/Expired Token', headers={"WWW-Authenticate": "Bearer"})
    try:
        user_id_int = int(user_id)
    except(TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid/Expired Token")
    
    result = await db.execute(select(User).where(User.id==user_id_int))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User NOT Found',  headers={"WWW-Authenticate": "Bearer"})
    
    return user



CurrentUser = Annotated[User, Depends(get_current_user)]
