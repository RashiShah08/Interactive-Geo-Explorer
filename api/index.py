"""Vercel entrypoint.

Vercel turns each file under /api into a serverless function and serves an ASGI
`app` if the module exposes one. The real application lives in server/main.py;
this is only the hook Vercel looks for.
"""
import sys
from pathlib import Path

# The function runs with /api as its working directory, so make the repo root
# importable for `server.*` and `src.*`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server.main import app  # noqa: E402

__all__ = ["app"]
