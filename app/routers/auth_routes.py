"""
Authentication routes for user registration, login, token refresh,
and retrieving the current authenticated user.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from models.models import Users
from schemas.userschema import UserCreate, UserResponse
from schemas.authschema import LoginRequest, RefreshTokenRequest
from services.auth_service import (
    register_user,
    authenticate_user,
    refresh_access_token,
)
from utils.dependencies import get_current_user
from schemas.authschema import SetPasswordRequest
from services.auth_service import set_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    return register_user(db, user)


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return access and refresh tokens."""
    return authenticate_user(db, request.email, request.password)


@router.post("/refresh")
def refresh_token(request: RefreshTokenRequest):
    """Authenticate a user and return access and refresh tokens."""
    return refresh_access_token(request.refresh_token)

@router.post("/set-password")
def set_password_endpoint(
    request: SetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    Set a password for an SSO-only account.
    """
    return set_password(db, current_user, request.password)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Users = Depends(get_current_user)):
    """Return details of the currently authenticated user."""
    return current_user
