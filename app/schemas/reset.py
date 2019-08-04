from pydantic import BaseModel
from datetime import datetime


class Reset(BaseModel):
    id: int
    userId: int
    createdTime: datetime
    expireTime: datetime
    isValid: bool

    class Config:
        orm_mode = True
