# schemas/user.py

import uuid
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr = Field(..., example="johndoe@example.com")
    first_name: str = Field(..., min_length=1, example="John")
    last_name: str = Field(..., min_length=1, example="Doe")
    phone: Optional[float] = Field(None, example=1234567890)
    google_id: Optional[str] = Field(None, example="")
    is_active: bool = Field(True, example=True)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="aSecurePassword123")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, example="johndoe_new@example.com")
    first_name: Optional[str] = Field(None, min_length=1, example="John")
    last_name: Optional[str] = Field(None, min_length=1, example="Doe")
    password: Optional[str] = Field(None, min_length=8, example="anotherSecurePassword456")
    is_active: Optional[bool] = Field(None, example=False)

class User(UserBase):
    id: uuid.UUID
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 