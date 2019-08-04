import uuid

import jwt
import pendulum
from passlib.hash import argon2
from sqlalchemy import BigInteger, Boolean, Column, DateTime, String
from config import get_config
from models.base import Base

app_config = get_config()


class User(Base):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True)
    firstName = Column(String(50), nullable=True, default=None)
    lastName = Column(String(50), nullable=True, default=None)
    emailAddress = Column(String(80), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    createdTime = Column(DateTime, nullable=False)
    modifiedTime = Column(DateTime, nullable=False)
    UUID = Column(String(36), nullable=False, default=uuid.uuid4())
    phoneNumber = Column(String(14), nullable=True, default=None)
    isVerified = Column(Boolean, nullable=False, default=False)
    userRole = Column(String(14), nullable=False, default="USER")

    def __init__(
        self,
        emailAddress,
        password,
        firstName=None,
        lastName=None,
        phoneNumber=None,
        userRole="USER",
        isVerified=False,
    ):
        now = pendulum.now("UTC")
        self.firstName = firstName
        self.lastName = lastName
        self.emailAddress = emailAddress
        self.password = password
        self.phoneNumber = phoneNumber
        self.userRole = userRole
        self.isVerified = isVerified
        self.createdTime = now
        self.modifiedTime = now

    def __str__(self):
        return "id: {} email: {}".format(self.id, self.emailAddress)

    def gen_token(self, expire_hours=app_config.TOKEN_TTL_HOURS):
        payload = {
            "userId": self.id,
            "exp": pendulum.now("UTC").add(hours=int(expire_hours)),
        }
        return str(
            jwt.encode(payload, app_config.JWT_SECRET, app_config.JWT_ALGORITHM).decode(
                "utf-8"
            )
        )

    def pass_matches(self, postPass):
        return argon2.verify(postPass, self.password)
