from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from backend.app.schemas.user import UserRead
from backend.app.services.auth_service import AuthService
from backend.app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email and password to receive JWT access and refresh tokens."""
    return AuthService.login(db, payload.email, payload.password)


@router.post("/refresh")
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a fresh access token."""
    token, expires_in = AuthService.refresh_access_token(db, payload.refresh_token)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


@router.get("/me", response_model=UserRead)
def get_current_authenticated_user(current_user: User = Depends(get_current_user)):
    """Retrieve details for the currently logged in user."""
    return current_user


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user)):
    """Acknowledge client logout and invalidate session on client side."""
    return {"message": "Logged out successfully."}
