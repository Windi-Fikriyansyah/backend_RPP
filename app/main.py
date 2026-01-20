import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

from app.database import init_db, engine, Base
from app.config import Config
from app.models import user, curriculum, rpp_data, payment # Import all models here
from app.routes import auth, rpp, curriculum, payment

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Init DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown

app = FastAPI(title="RPP AI Backend", lifespan=lifespan)

# Global Exception Handler to ensure CORS headers are present even on 500 errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Global Exception: {exc}", exc_info=True)
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "message": str(exc)},
    )
    # Re-add CORS headers manually for the error response
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# 1. Proxy & Session Middleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.add_middleware(
    SessionMiddleware, 
    secret_key=Config.SECRET_KEY, 
    max_age=3600*24 * 7, # 7 Days
    https_only=Config.ENV == "PRODUCTION",
    same_site="lax",
    domain=Config.SESSION_COOKIE_DOMAIN
)

# 2. CORS
origins = [
    Config.FRONTEND_URL,
    "https://rppgenius.sekolahliterasi.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Allow Cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(rpp.router, prefix="/api/rpp", tags=["RPP"])
app.include_router(curriculum.router) # Prefix defined in router
app.include_router(payment.router, prefix="/api/payment", tags=["Payment"])

@app.get("/")
def root():
    return {"message": "RPP AI Backend Online"}
