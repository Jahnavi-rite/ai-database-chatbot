import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from auth.models import User
from auth.utils import hash_password

logger = logging.getLogger(__name__)

DEFAULT_USERS = [
    {"username": "admin", "password": "admin123", "role": "admin"},
    {"username": "user", "password": "user123", "role": "user"},
]


def seed_users():
    db: Session = SessionLocal()
    try:
        for u in DEFAULT_USERS:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if existing:
                logger.debug(f"User '{u['username']}' already exists, skipping")
                continue
            user = User(
                username=u["username"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(user)
            logger.info(f"Seeded user: {u['username']} (role={u['role']})")
        db.commit()
        logger.info("User seeding complete")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding users: {e}")
    finally:
        db.close()
