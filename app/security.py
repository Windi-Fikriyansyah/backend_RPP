from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt_sha256", "bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

from fastapi import Request, HTTPException

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_current_user_id(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized. Please login.")
    return user_id
