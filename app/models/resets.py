import uuid

import pendulum
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from config import get_config
from models.base import Base

appConfig = get_config()


class PasswordReset(Base):
    __tablename__ = "PasswordReset"
    id = Column(BigInteger, primary_key=True)
    UUID = Column(String(36), nullable=False, default=uuid.uuid4())
    userId = Column(BigInteger, ForeignKey("User.id"), nullable=False)
    createdTime = Column(DateTime, nullable=False, default=pendulum.now("UTC"))
    expireTime = Column(
        DateTime,
        nullable=False,
        default=pendulum.now("UTC").add(
            hours=int(appConfig.PASSWORD_RESET_LINK_TTL_HOURS)
        ),
    )
    isValid = Column(Boolean, nullable=False, default=True)

    def __init__(self, userId):
        self.userId = userId
