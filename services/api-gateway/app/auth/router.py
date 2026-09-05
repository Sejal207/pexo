from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.auth.models import AppUser, Role
from app.auth.schemas import UserLogin, UserSignup, TokenResponse, UserOut
from app.auth.jwt_handler import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserOut)
async def signup(user_in: UserSignup, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppUser).filter(AppUser.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = AppUser(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppUser).filter(AppUser.email == user_in.email))
    user = result.scalars().first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "roles": [r.name for r in user.roles]
    }
    token = create_access_token(token_data)
    return TokenResponse(access_token=token)
