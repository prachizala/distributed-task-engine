from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    create_access_token,
    get_db_session,
    get_password_hash,
    verify_password,
)
from app.config import settings
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserOut

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)):
    stmt = select(User).where((User.email == user_in.email) | (User.username == user_in.username))
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )

    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        role=user_in.role,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_session)
):
    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": role_str}, expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
