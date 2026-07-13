from typing import Annotated

from datetime import timedelta, UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query


from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import delete as sql_delete

from Databases.UserDB.database import get_db

from Schema.schema import UserBase, UserCreate, UserPrivate, UserPublic, UserUpdate, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest, LoginRequest

from Models.models import User, PasswordResetToken

from backend.auth import create_access_token, hash_password, verify_hash_password, verify_access_tokens, CurrentUser
from backend.config import settings

from fastapi import BackgroundTasks

from backend.auth import generate_reset_token, hash_reset_token


router = APIRouter()

# Creating / Register a NEW USER in USERDB ->
@router.post("/register", response_model=UserPrivate)
async def register_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(func.lower(User.username)==user.username.lower()))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='USERNAME already exists')

    result = await db.execute(select(User.email).where(func.lower(User.email)==user.email.lower()))
    existing_email = result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='EMAIL already exists')
    
    new_user = User(
        username = user.username,
        email = user.email,
        password_hashed = hash_password(user.password)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# Token Response ->
@router.post("/login", response_model=TokenResponse)
async def login_for_access_tokens(credentials: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(func.lower(User.username)==credentials.username.lower()))
    user = result.scalars().first()

    if not user or not verify_hash_password(credentials.password, user.password_hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Email/Password", headers={'WWW-Authenticate': 'Bearer'})
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token=create_access_token(data={'sub': str(user.id)}, expires_delta=access_token_expires)
    return TokenResponse(access_token=access_token, token_type='bearer')
    

# Updating partial sections of User in UserDB ->
@router.patch("/{user_id}/update", response_model=UserPrivate)
async def update_user_partial(user_id: int, user_update: UserUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to update this user')
    
    result = await db.execute(select(User).where(User.id==user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found')
    
    if user_update.username is not None and user_update.username.lower() != user.username.lower():
        result = await db.execute(select(User).where(func.lower(User.username)==user_update.username.lower()))
        existing_username = result.scalar_one_or_none()
        if existing_username: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='USERNAME already exists')
        
    if user_update.email is not None and user_update.email.lower() != user.email.lower():
        result = await db.execute(select(User).where(func.lower(User.email)==user_update.email.lower()))
        existing_email = result.scalar_one_or_none()
        if existing_email: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='EMAIL already exists')
        
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email.lower()

    await db.commit()
    await db.refresh(user)
    return user


# Deleting User from UserDB ->
@router.delete("/{user_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to delete this user')
    
    result = await db.execute(select(User).where(User.id==user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User NOT Found')
    
    # old_filename = user.img_file

    await db.delete(user)
    await db.commit()

    # if old_filename:
    #     delete_profile_img(old_filename)


# Forgot Password ->
@router.post("/login/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(request_data: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(func.lower(User.email)==request_data.email.lower()))
    user = result.scalars().first()

    if user:
        await db.execute(sql_delete(PasswordResetToken).where(PasswordResetToken.user_id==user.id))

        token = generate_reset_token()
        token_hash = hash_reset_token(token)
        expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        db.add(reset_token)
        await db.commit()

        background_tasks.add_task(
            # send_password_reset_email,
            to_email=user.email,
            username=user.username,
            token=token
        )

        return {
        "message": "If an account exists with this email, you will receive password reset instructions."
    }


# User Account ->
@router.get("/{user_id}/account", response_model=UserPrivate)
async def get_account(user_id: int, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return current_user


# Change Password ->
@router.patch("/{user_id}/account/change-password", status_code=status.HTTP_200_OK)
async def change_password(user_id: int, body: ChangePasswordRequest, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')

    if not verify_hash_password(body.current_password, current_user.password_hashed):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Current password is incorrect')

    current_user.password_hashed = hash_password(body.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}


# Reset Password ->
@router.post("/login/reset-password", status_code=status.HTTP_202_ACCEPTED)
async def reset_password(request_data: ResetPasswordRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    token_hash = hash_reset_token(request_data.token)
    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.token_hash==token_hash))
    reset_token = result.scalars().first()

    if not reset_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid/Expired Reset Token")

    if reset_token.expires_at < datetime.now(UTC):
        await db.delete(reset_token)
        await db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid/Expired Reset Token")
    
    result = await db.execute(select(User).where(User.id==reset_token.user_id))

    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid/Expired Reset Token")
    
    user.password_hashed = hash_password(request_data.new_password)

    await db.execute(sql_delete(PasswordResetToken).where(PasswordResetToken.user_id==user.id))

    await db.commit()
    return{
        "message": "Password has been reset successfully"
    }






