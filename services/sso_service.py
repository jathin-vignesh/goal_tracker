import os
import httpx
from jose import jwt
from sqlalchemy.orm import Session

from models.models import Users, UserAuthProviders
from utils.security import create_access_token, create_refresh_token
from fastapi import HTTPException

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/auth/google/callback"

async def handle_google_callback(db: Session, code: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
            },
        )

    token_data = resp.json()
    id_token = token_data.get("id_token")
    if not id_token:
        raise HTTPException(400, "Invalid Google response")

    payload = jwt.get_unverified_claims(id_token)

    provider_user_id = payload["sub"]
    email = payload["email"]

    provider = (
        db.query(UserAuthProviders)
        .filter_by(provider="google", provider_user_id=provider_user_id)
        .first()
    )

    if provider:
        user = provider.user
    else:
        user = db.query(Users).filter_by(email=email).first()
        if not user:
            user = Users(email=email, username=email.split("@")[0])
            db.add(user)
            db.flush()

        provider = UserAuthProviders(
            user_id=user.id,
            provider="google",
            provider_user_id=provider_user_id,
        )
        db.add(provider)

    db.commit()

    return {
        "access_token": create_access_token({"user_id": user.id}),
        "refresh_token": create_refresh_token({"user_id": user.id}),
        "token_type": "bearer",
    }
