from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from server.routers import chat, places

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"

app = FastAPI(
    title="Interactive Geo Explorer",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Nothing is user-specific: no accounts, no sessions, no secrets to configure.
# The frontend is served from this same app, so there is no CORS boundary either.
app.include_router(places.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

app.mount("/images", StaticFiles(directory=FRONTEND_DIR / "images"), name="images")
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(INDEX_FILE)
