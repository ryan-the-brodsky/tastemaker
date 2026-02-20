"""
Premium subscription check dependency.

Provides a FastAPI dependency that gates endpoints behind a premium subscription.
"""
from fastapi import Depends, HTTPException, status
from models import UserModel
from auth_routes import get_current_user


def require_premium(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """
    FastAPI dependency that requires the current user to have a premium subscription.

    Raises 403 if the user's subscription_tier is not "premium".
    """
    if current_user.subscription_tier != "premium":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    return current_user
