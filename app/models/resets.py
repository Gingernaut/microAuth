import uuid

import jwt
import pendulum
from passlib.hash import argon2
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String

import ujson
from config import get_config
from models.base import Base

appConfig = get_config()


class PasswordReset(Base):
    __tablename__ = "PasswordReset"
    id = Column(String(36), primary_key=True, default=uuid.uuid4())
    userId = Column(BigInteger, ForeignKey("User.id"), nullable=False)
    createdTime = Column(DateTime, nullable=False, default=pendulum.utcnow)
    expireTime = Column(
        DateTime,
        nullable=False,
        default=pendulum.utcnow().add(
            hours=int(appConfig.PASSWORD_RESET_LINK_TTL_HOURS)
        ),
    )
    isValid = Column(Boolean, nullable=False, default=True)

    def __init__(self, userId):
        self.userId = userId
