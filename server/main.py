import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from server.routers import auth, chat, places

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"

SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
if not SESSION_SECRET_KEY:
    raise RuntimeError(
        "SESSION_SECRET_KEY is not set. Copy .env.example to .env and set it "
        "(generate one with: python -c \"import secrets; print(secrets.token_hex(32))\")."
    )

app = FastAPI(title="Interactive Geo Explorer", docs_url="/api/docs", openapi_url="/api/openapi.json")

# Same-origin frontend, so no CORS middleware is needed.
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    session_cookie="geo_session",
    same_site="lax",
    https_only=False,
)

app.include_router(auth.router, prefix="/api")
app.include_router(places.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

app.mount("/images", StaticFiles(directory=FRONTEND_DIR / "images"), name="images")
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(INDEX_FILE)
