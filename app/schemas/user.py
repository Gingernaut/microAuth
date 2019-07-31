from pydantic import BaseModel, Schema
from uuid import UUID
from config import get_config
from datetime import datetime

app_config = get_config()


class UserBase(BaseModel):
    firstName: str = None
    lastName: str = None
    emailAddress: str
    phoneNumber: str = None


class UserCreate(UserBase):
    emailAddress: str
    password: str = Schema(..., min_length=app_config.MIN_PASS_LENGTH)
    firstName: str = None
    lastName: str = None
    phoneNumber: str = None


class User(UserBase):
    id: int
    createdTime: datetime
    modifiedTime: datetime
    UUID: UUID
    isVerified: bool
    userRole: str

    class Config:
        orm_mode = True


# All optional fields that can but updated via PUT
class UserUpdate(UserBase):
    emailAddress: str = None
    isVerified: bool = None
    userRole: str = None
    password: str = Schema(None, min_length=app_config.MIN_PASS_LENGTH)

    class Config:
        orm_mode = True


class LoggedInUser(User):
    jwt: str

    class Config:
        orm_mode = True
