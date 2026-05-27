import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.models import User
from auth.schemas import LoginRequest, TokenResponse, UserResponse
from auth.utils import verify_password, create_access_token
from auth.dependencies import get_db, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user='{request.username}'")

    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        logger.warning(f"Login failed — user '{request.username}' not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    if not verify_password(request.password, user.hashed_password):
        logger.warning(f"Login failed — wrong password for user='{request.username}'")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = create_access_token({"sub": user.username, "role": user.role})
    logger.info(f"Login successful — user='{user.username}' role='{user.role}'")

    return TokenResponse(access_token=token, role=user.role, username=user.username)


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    logger.info(f"Profile requested for user='{user.username}'")
    return user
