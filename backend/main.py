import os
import sys
from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from alembic.config import Config
from alembic import command

from routers import auth, emails, insights

# Automatically run Alembic migrations on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Migrations should be run manually or in a separate pre-start script
    yield

SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key-must-be-changed")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

app = FastAPI(title="SpendLens API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session",
    max_age=14 * 24 * 60 * 60,
    same_site="lax",
    https_only=False, # Set to True in Production
)

app.include_router(auth.router)
app.include_router(emails.router)
app.include_router(insights.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
