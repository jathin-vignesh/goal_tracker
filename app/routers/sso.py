from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
import httpx

from db import get_db
from services.sso_service import handle_google_callback

router = APIRouter(prefix="/auth/google")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
REDIRECT_URI = "http://localhost:8000/auth/google/callback"
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

@router.get("/login")
def google_login():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": REDIRECT_URI,
        "prompt": "select_account",
    }
    return RedirectResponse(httpx.URL(GOOGLE_AUTH_URL, params=params))

@router.get("/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(400, "Missing code")

    return await handle_google_callback(db, code)
