from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    roles: List[str] = ["EMPLOYEE"]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    roles: List[str] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
