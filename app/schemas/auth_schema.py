from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    google_id: Optional[str] = None
    subscription_plan: Optional[str] = "free" # 'free', 'pro', 'school'

    class Config:
        from_attributes = True
