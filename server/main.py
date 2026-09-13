from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
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

# Serve the frontend ourselves when the files are alongside us, which is the
# case locally and on any host running this as a normal process. On a CDN-backed
# deploy the static routes never reach Python and the directory may not be in
# the function bundle at all, so mounting is conditional rather than assumed.
for folder in ("images", "css", "js", "brand"):
    directory = FRONTEND_DIR / folder
    if directory.is_dir():
        app.mount(f"/{folder}", StaticFiles(directory=directory), name=folder)


@app.get("/", include_in_schema=False)
def index():
    if INDEX_FILE.is_file():
        return FileResponse(INDEX_FILE)
    # The CDN owns this route in that case; reaching here means a routing slip.
    return JSONResponse(
        {"detail": "Frontend is served separately; the API lives under /api."},
        status_code=404,
    )
