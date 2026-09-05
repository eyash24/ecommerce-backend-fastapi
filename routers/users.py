from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks
)

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete as sql_delete
from sqlalchemy import or_

import models
from database import get_ecommerce_db
from schema.users import(
    UserCreate,
    UserUpdate,
    UserPublic,
    UserPrivate
)
from schema.auth import (
    Token,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

from datetime import timedelta, UTC, datetime
from fastapi.security import OAuth2PasswordRequestForm

from auth import (
    CurrentUser,
    create_access_token,
    hash_password,
    verify_password,
    generate_reset_token,
    hash_reset_token
)

from config import settings

from utils.email_utils import send_password_reset_mail


router = APIRouter()

@router.post(
    '',
    response_model=UserPrivate,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate, 
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.User).where(
            or_(
                func.lower(models.User.username) == user.username.lower(),
                func.lower(models.User.email) == user.email.lower()
            )
            
        )
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Account already exist'
        )
    
    new_user = models.User(
        username = user.username,
        email = user.email.lower(),
        password_hash = hash_password(user.password),
        image_url = user.image_url
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.email) == form_data.username.lower(),
        ),
    )
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )


    access_token_expires = timedelta(minutes = settings.access_token_expire_minutes)
    access_token = create_access_token(
        data = {'sub': str(user.id)},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type='bearer')


@router.get('/me', response_model=UserPrivate)
async def get_current_user(current_user: CurrentUser):
    return current_user


@router.post('/forgot-password', status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.email) == request_data.email.lower(),
        )
    )
    user= result.scalars().first()

    if user:
        await db.execute(
            sql_delete(models.PasswordResetToken).where(
                models.PasswordResetToken.user_id == user.id
            )
        )

        token = generate_reset_token()
        token_hash = hash_reset_token(token)
        expires_at = datetime.now(UTC) + timedelta(
            minutes = settings.reset_token_expire_minutes
        )

        reset_token = models.PasswordResetToken(
            user_id = user.id,
            token_hash = token_hash,
            expired_at = expires_at
        )

        db.add(reset_token)
        await db.commit()

        background_tasks.add_task(
            send_password_reset_mail,
            to_email=user.email,
            username=user.username,
            token=token
        )

    return {
        "message": "If an account exist with this email, you will receive password reset instructions."
    }
    

@router.post('/reset-password', status_code=status.HTTP_200_OK)
async def reset_password(
    request_data: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    token_hash = hash_reset_token(request_data.token)

    result = await db.execute(
        select(models.PasswordResetToken)
        .where(models.PasswordResetToken.token_hash == token_hash)
    )

    reset_token = result.scalars().first()

    if not reset_token:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail='Invalid or expired reset token'
        )

    if reset_token.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
        await db.delete(reset_token)
        await db.commit()
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail='Invalid or expired reset token'
        )

    result = await db.execute(
        select(models.User)
        .where(models.User.id == reset_token.user_id)
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid or expired reset token'
        )

    user.password_hash = hash_password(request_data.new_password)

    await db.commit()
    return {
        "message": "Password reset successful. You can log in with new password."
    }


@router.patch('/me/password', status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail='Current password is incorrect'
        )

    current_user.password_hash = hash_password(password_data.new_password)

    await db.execute(
        sql_delete(models.PasswordResetToken)
        .where(models.PasswordResetToken.user_id == current_user.id)
    )

    await db.commit()
    return {'message': 'Password changed successfully'}


@router.get('/{user_id}', response_model=UserPublic)
async def get_user(user_id:int, db: Annotated[AsyncSession, Depends(get_ecommerce_db)]):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    user = result.scalars().first()

    if user:
        return user

    raise HTTPException(
       status_code=status.HTTP_404_NOT_FOUND,
       detail="User not found"
    )


#TODO: Take reference of product update and improve the below function
@router.patch('/{user_id}', response_model=UserPrivate)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorised to update this user'
        )

    result = await db.execute(
        select(models.User)
        .where(models.User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    if (
        user_update.username is not None
        and user_update.username.lower() != user.username.lower()
    ):
        result = await db.execute(
            select(models.User)
            .where(func.lower(models.User.username) == user_update.username.lower())
        )
        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username already exist'
            )

        if user_update.email is not None and user_update.email.lower() != user.email.lower():
            result = await db.execute(
                select(models.User)
                .where(func.lower(models.User.email) == user_update.email.lower())
            )

            existing_email = result.scalars().first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Email already exist'
                )

            if user_update.username is not None:
                user.username = user_update.username
            if user_update.email is not None:
                user.email = user_update.email.lower()
            if user_update.image_url is not None:
                user.image_url = user_update.image_url

            await db.commit()
            await db.refresh(user)
            return user


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_ecommerce_db)]
):


    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorised to delete user'
        )

    await db.delete(user)
    await db.commit()
