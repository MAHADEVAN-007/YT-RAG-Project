from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi import HTTPException, status

from contextlib import asynccontextmanager

from Databases.UserDB.database import engine, Base

from Models.models import User

from Schema.schema import UserPublic

from backend.auth import get_current_user
from backend.routers.users import router as users_router
from backend.routers.youtube import router as youtube_router

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(youtube_router)


TEMPLATES_DIR = FRONTEND_DIR / "templates"


@app.get("/")
async def serve_index():
    html = (TEMPLATES_DIR / "login.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/register")
async def serve_register():
    html = (TEMPLATES_DIR / "register.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/login")
async def serve_login():
    html = (TEMPLATES_DIR / "login.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/home")
async def home():
    return {
        "name": "YT-RAG",
        "description": "Paste a YouTube URL, get transcripts, and ask questions using AI",
        "version": "0.1.0",
    }


@app.get("/{user_id}/me", response_model=UserPublic)
async def user_profile(user_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    from fastapi import HTTPException
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot access another user's profile")
    return current_user


@app.get("/dashboard")
async def serve_dashboard():
    html = (TEMPLATES_DIR / "dashboard.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/account")
async def account_page():
    html = (TEMPLATES_DIR / "account.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


