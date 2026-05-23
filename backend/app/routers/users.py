from fastapi import APIRouter, Depends
from ..schemas import UserRead
from ..security import get_current_user

router = APIRouter()

@router.get("/me", response_model = UserRead)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user

"""
    Returns the public profile of the **authenticated** user.
    The `get_current_user` dependency performs:
        • JWT verification
        • DB lookup of the user record
        • Raises 401 if anything is invalid
    Because the dependency returns a full SQLModel/SQLAlchemy `User` object,
    we can simply return it – FastAPI will automatically convert it to the
    `UserRead` Pydantic model you defined in `schemas.py`.
"""