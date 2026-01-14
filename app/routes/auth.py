from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi_sso.sso.google import GoogleSSO
import os

from app.database import get_db
from app.models.user import User
from app.schemas.auth_schema import UserCreate, UserLogin, UserResponse
from app.security import get_password_hash, verify_password

router = APIRouter()

# Setup Google SSO
from app.config import Config
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# PENTING: redirect_uri harus sama dengan di google console
# Gunakan BACKEND_URL dari config jika GOOGLE_REDIRECT_URI tidak diset
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", f"{Config.BACKEND_URL}/auth/google/callback")
print(f"DEBUG: Config.FRONTEND_URL = {Config.FRONTEND_URL}")
print(f"DEBUG: Config.BACKEND_URL = {Config.BACKEND_URL}")
print(f"DEBUG: GOOGLE_REDIRECT_URI = {GOOGLE_REDIRECT_URI}")

google_sso = GoogleSSO(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_uri=GOOGLE_REDIRECT_URI,
    allow_insecure_http=os.getenv("ENV") != "PRODUCTION" # Disable insecure HTTP in production
)

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check existing
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(request: Request, user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Set Session Cookie
    request.session["user_id"] = user.id
    return {"message": "Login successful", "user": {"id": user.id, "email": user.email}}

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}

@router.get("/google/login")
async def google_login():
    return await google_sso.get_login_redirect()

@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        user_info = await google_sso.verify_and_process(request)
    except Exception as e:
         raise HTTPException(status_code=400, detail=str(e))
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_info.email))
    user = result.scalar_one_or_none()

    if not user:
        # Create user via Google
        user = User(
            email=user_info.email,
            full_name=user_info.display_name,
            google_id=user_info.id,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Link google_id if not linked
        if not user.google_id:
            user.google_id = user_info.id
            db.add(user)
            await db.commit()

    # Set Session
    request.session["user_id"] = user.id
    
    # Redirect to Frontend
    # Ganti URL ini dengan URL Frontend Next.js Anda (misal halaman dashboard / generator)
    # Karena API dan Frontend beda port di dev, kita redirect absolutely.
    # Jika perlu kirim data, biasanya set cookie sudah cukup, frontend cek /me
    from starlette.responses import RedirectResponse
    from app.config import Config
    frontend_url = Config.FRONTEND_URL # URL Next.js
    return RedirectResponse(url=frontend_url)

@router.get("/me", response_model=UserResponse)
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        request.session.clear()
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check Subscription
    from app.models.payment import Subscription
    from app.utils.time_utils import get_jakarta_time
    
    sub_res = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.is_active == True,
            Subscription.end_date > get_jakarta_time()
        )
    )
    subscription = sub_res.scalars().first()
    
    # Attach plan type to user object for UserResponse mapping
    raw_plan = subscription.plan_type if subscription else "free"
    
    # Map 'monthly' and 'yearly' to 'pro' for easier frontend handling
    if raw_plan in ["monthly", "yearly"]:
        user.subscription_plan = "pro"
    else:
        user.subscription_plan = raw_plan
    
    return user
