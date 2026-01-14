import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost/rpp_dp")
    SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_locally")
    
    # TRIPAY CONFIG
    TRIPAY_API_KEY = os.getenv("TRIPAY_API_KEY", "DEV-...")
    TRIPAY_PRIVATE_KEY = os.getenv("TRIPAY_PRIVATE_KEY", "...") # Private Key for Signature
    TRIPAY_MERCHANT_CODE = os.getenv("TRIPAY_MERCHANT_CODE", "T12345")
    TRIPAY_MODE = os.getenv("TRIPAY_MODE", "SANDBOX") # SANDBOX or PRODUCTION
    
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
