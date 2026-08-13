from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies import get_auth_service
from app.models.schemas import AuthCredentials, AuthRegisterRequest, AuthResponse
from app.services.auth_service import AuthService, RateLimitExceeded

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _client_ip(request: Request) -> str:
    client = request.client
    return client.host if client else "unknown"


def _normalize_email(email: str) -> str:
    return email.strip().lower()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: Request, payload: AuthRegisterRequest, auth_service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    try:
        request_key = auth_service.derive_rate_limit_key(
            endpoint="register",
            client_ip=_client_ip(request),
        )
        auth_service.enforce_rate_limit(endpoint="register", request_key=request_key)
        return AuthResponse(**auth_service.register(**payload.model_dump()))
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please retry later.",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=AuthResponse)
def login(request: Request, payload: AuthCredentials, auth_service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    try:
        request_key = auth_service.derive_rate_limit_key(
            endpoint="login",
            client_ip=_client_ip(request),
            normalized_email=_normalize_email(payload.email),
        )
        auth_service.enforce_rate_limit(endpoint="login", request_key=request_key)
        return AuthResponse(**auth_service.login(**payload.model_dump()))
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please retry later.",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.") from exc


@router.post("/logout")
def logout(request: Request, auth_service: AuthService = Depends(get_auth_service)) -> dict[str, str]:
    credentials = request.headers.get("Authorization", "")
    if not credentials.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required.")
    token = credentials.split(" ", 1)[1].strip()
    try:
        auth_service.logout(token)
        return {"detail": "Logout successful."}
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated principal is invalid.")