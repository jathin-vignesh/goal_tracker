"""Authentication services for user registration, login, and token refresh."""

from sqlalchemy.orm import Session
import bcrypt
from fastapi import HTTPException, status
from models.models import Users
from schemas.userschema import UserCreate, UserResponse
from utils.security import create_access_token, create_refresh_token, decode_refresh_token


# PASSWORD HASHING UTILITIES
def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    password_bytes = password.strip().encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    plain_bytes = plain_password.strip().encode("utf-8")[:72]
    return bcrypt.checkpw(plain_bytes, hashed_password.encode("utf-8"))


# USER REGISTRATION
def register_user(db: Session, user: UserCreate) -> UserResponse:
    """
    Register a new user using email + password.

    Rules:
    - Email must be unique
    - Username must be unique
    - If email already exists via SSO, block password registration
    """

    # Check email
    existing_user = (
        db.query(Users)
        .filter(Users.email == user.email)
        .first()
    )

    if existing_user:
        # Case 1: User already has password → normal duplicate
        if existing_user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Case 2: User exists via SSO only
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already exists via SSO. Please login using Google."
        )

    # Check username
    existing_username = (
        db.query(Users)
        .filter(Users.username == user.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Hash password
    hashed_password = hash_password(user.password)

    # Create user
    db_user = Users(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user



# USER AUTHENTICATION
def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user and return access and refresh tokens."""
    user = db.query(Users).filter(Users.email == email).first()

    if (
        not user
        or not user.password_hash  # 🔒 SSO-only user
        or not verify_password(password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
    }



# TOKEN REFRESH
def refresh_access_token(refresh_token: str):
    """Generate a new access token using a valid refresh token."""
    payload = decode_refresh_token(refresh_token)
    new_access_token = create_access_token({"user_id": payload["user_id"]})
    return {"access_token": new_access_token, "token_type": "bearer"}

def set_password(db: Session, user: Users, password: str):
    """
    Allow an SSO-only user to set a password.

    Rules:
    - User must be authenticated
    - User must NOT already have a password
    """
    if user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password already set for this account"
        )

    hashed_password = hash_password(password)
    user.password_hash = hashed_password

    db.commit()
    db.refresh(user)

    return {"message": "Password set successfully"}
