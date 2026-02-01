"""
Single-user mode support for TasteMaker.

When SINGLE_USER_MODE=true, the application skips authentication and
automatically uses a local user account. This simplifies deployment
for personal/local use.
"""
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from db_config import SessionLocal
from models import UserModel

# Password hasher (same as auth_routes)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Constants for the single user
SINGLE_USER_ID = "local-user-001"
SINGLE_USER_EMAIL = "local@tastemaker.local"
SINGLE_USER_FIRST_NAME = "Local"
SINGLE_USER_LAST_NAME = "User"


def get_or_create_single_user(db: Session) -> UserModel:
    """
    Get or create the single local user account.

    This user is automatically created when running in single-user mode.
    """
    # Try to find existing user
    user = db.query(UserModel).filter(UserModel.id == SINGLE_USER_ID).first()

    if user:
        return user

    # Create the single user
    user = UserModel(
        id=SINGLE_USER_ID,
        email=SINGLE_USER_EMAIL,
        password_hash=pwd_context.hash("single-user-mode"),  # Not used, but required
        first_name=SINGLE_USER_FIRST_NAME,
        last_name=SINGLE_USER_LAST_NAME,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_single_user() -> UserModel:
    """
    Get the single user, creating if necessary.

    This is a convenience function that manages its own database session.
    """
    db = SessionLocal()
    try:
        return get_or_create_single_user(db)
    finally:
        db.close()
