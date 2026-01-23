"""Authentication endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.main import WEB_AUTH_ENABLED, WEB_SECRET_KEY

router = APIRouter()
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str


class User(BaseModel):
    username: str


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, WEB_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """Get current user from JWT token"""
    if not WEB_AUTH_ENABLED:
        return User(username="admin")

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, WEB_SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return User(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    # Simple auth - in production use proper password hashing
    if request.username == "admin" and request.password == "admin":
        access_token = create_access_token(data={"sub": request.username})
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            username=request.username,
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@router.get("/enabled")
async def auth_enabled():
    """Check if authentication is enabled"""
    return {"enabled": WEB_AUTH_ENABLED}
