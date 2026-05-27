import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
from auth.models import User
from auth.utils import decode_access_token

logger = logging.getLogger(__name__)
security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if not username:
            logger.warning("JWT token missing 'sub' claim")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception:
        logger.warning("Authentication failed — invalid or expired token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        logger.warning(f"User '{username}' not found in database")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    logger.debug(f"Authenticated user: {user.username} (role={user.role})")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        logger.warning(f"Admin access denied for user={user.username} role={user.role}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    logger.debug(f"Admin access granted for user={user.username}")
    return user


def require_write_access(user: User = Depends(get_current_user)) -> User:
    """Only admin users can perform write (INSERT/UPDATE/DELETE) operations."""
    if user.role != "admin":
        logger.warning(f"Write access denied for user={user.username} role={user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Read-only access. Only administrators can modify data.",
        )
    logger.debug(f"Write access granted for user={user.username}")
    return user
