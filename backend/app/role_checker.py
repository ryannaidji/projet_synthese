from typing import Annotated
from app.models import User
from fastapi import Depends
from app.auth import get_current_active_user
from app.schemas import UserResponse, UserCreate

class RoleChecker:
  def __init__(self, allowed_roles):
    self.allowed_roles = allowed_roles

  def __call__(self, user: Annotated[User, Depends(get_current_active_user)]):
    if user.role in self.allowed_roles:
      return True
    raise HTTPException(
status_code=status.HTTP_401_UNAUTHORIZED,
detail="You don't have enough permissions")

