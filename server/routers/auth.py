from fastapi import APIRouter, Depends, Request, Response, status

from server.deps import get_current_user
from server.schemas import AuthResult, Credentials
from src.auth.service import login as login_user
from src.auth.service import signup as signup_user

router = APIRouter(tags=["auth"])


@router.post("/signup", response_model=AuthResult)
def signup(payload: Credentials, response: Response) -> AuthResult:
    ok, message = signup_user(payload.username, payload.password)
    response.status_code = status.HTTP_201_CREATED if ok else status.HTTP_400_BAD_REQUEST
    return AuthResult(ok=ok, message=message)


@router.post("/login", response_model=AuthResult)
def login(payload: Credentials, request: Request, response: Response) -> AuthResult:
    ok, message = login_user(payload.username, payload.password)
    if not ok:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return AuthResult(ok=False, message=message)

    username = payload.username.strip()
    request.session["username"] = username
    return AuthResult(ok=True, message=message, username=username)


@router.post("/logout", response_model=AuthResult)
def logout(request: Request) -> AuthResult:
    request.session.clear()
    return AuthResult(ok=True, message="Signed out.")


@router.get("/me", response_model=AuthResult)
def me(username: str = Depends(get_current_user)) -> AuthResult:
    return AuthResult(ok=True, username=username)
