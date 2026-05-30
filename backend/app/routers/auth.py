import os
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import (
    Token,
    AuthResponse,
    UserCreateManual,
    UsernameCheckResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    GoogleLoginRequest,
)
from ..security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    decode_token,
)

router = APIRouter()


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    cookie_secure = os.getenv("ENV") == "production"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=cookie_secure,
        samesite="lax",
        max_age=15 * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=cookie_secure,
        samesite="lax",
        max_age=14 * 24 * 60 * 60,
        path="/",
    )


@router.post("/login", response_model=AuthResponse)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        (User.username == form_data.username) |
        (User.email == form_data.username)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password login not available for this account",
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(user_id=str(user.id))
    refresh_token = create_refresh_token(user_id=str(user.id))

    set_auth_cookies(response, access_token, refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreateManual,
    response: Response,
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    if len(user_data.password) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 10 characters long",
        )

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password_hash=get_password_hash(user_data.password),
        auth_provider="local",
        is_email_verified=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(user_id=str(new_user.id))
    refresh_token = create_refresh_token(user_id=str(new_user.id))
    set_auth_cookies(response, access_token, refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user,
    }


@router.post("/refresh", response_model=Token)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token_value = request.cookies.get("refresh_token")

    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    try:
        payload = decode_token(refresh_token_value)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh session",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    new_access_token = create_access_token(user_id=str(user.id))

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=os.getenv("ENV") == "production",
        samesite="lax",
        max_age=15 * 60,
        path="/",
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {
        "message": "Logged out successfully",
    }


@router.get("/username-available", response_model=UsernameCheckResponse)
def username_available(username: str, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.username == username).first() is not None
    return {
        "username": username,
        "available": not exists,
    }


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if user:
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires_at = datetime.utcnow() + timedelta(hours=1)
        db.commit()

        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        print(f"Password reset link: {reset_link}")

    return {
        "message": "If the email exists, password reset instructions have been sent.",
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.password_reset_token == payload.token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    if not user.password_reset_expires_at or user.password_reset_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired",
        )

    if len(payload.new_password) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 10 characters long",
        )

    user.password_hash = get_password_hash(payload.new_password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    db.commit()

    return {
        "message": "Password reset successful",
    }


@router.post("/google-login", response_model=AuthResponse)
def google_login(
    payload: GoogleLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not google_client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google client ID not configured",
        )

    try:
        google_info = id_token.verify_oauth2_token(
            payload.id_token,
            google_requests.Request(),
            google_client_id,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication failed",
        )

    email = google_info.get("email")
    google_sub = google_info.get("sub")
    first_name = google_info.get("given_name")
    last_name = google_info.get("family_name")
    email_verified = bool(google_info.get("email_verified", False))

    if not email or not google_sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google token",
        )

    user = db.query(User).filter(User.email == email).first()

    if user:
        user.google_sub = google_sub
        user.auth_provider = "both" if user.password_hash else "google"
        user.is_email_verified = email_verified
        if not user.first_name and first_name:
            user.first_name = first_name
        if not user.last_name and last_name:
            user.last_name = last_name
    else:
        user = User(
            email=email,
            username=None,
            first_name=first_name,
            last_name=last_name,
            password_hash=None,
            auth_provider="google",
            google_sub=google_sub,
            is_email_verified=email_verified,
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    access_token = create_access_token(user_id=str(user.id))
    refresh_token = create_refresh_token(user_id=str(user.id))
    set_auth_cookies(response, access_token, refresh_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }