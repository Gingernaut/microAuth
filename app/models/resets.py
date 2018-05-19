import uuid

import jwt
import pendulum
from passlib.hash import argon2
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String

import ujson
from config import get_config
from models.base import Base

appConfig = get_config()


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    createdDate = Column(DateTime, nullable=False, default=pendulum.utcnow)
    expireDate = Column(
        Datetime,
        nullable=False,
        default=pendulum.utcnow().add(hours=int(appConfig.RESET_HOURS)),
    )
    UUID = Column(String(36), nullable=False)
    isValidated = Column(Boolean, nullable=False, default=False)

    def __init__(
        self,
        emailAddress,
        password,
        firstName=None,
        lastName=None,
        phoneNumber=None,
        userRole="USER",
        isValidated=False,
    ):
        self.UUID = uuid.uuid4()
        self.lastName = lastName
        self.emailAddress = emailAddress
        self.password = password
        self.phoneNumber = phoneNumber
        self.userRole = userRole
        self.isValidated = isValidated

    def serialize(self, jwt=False):
        return {}

    def pass_matches(self, postPass):
        return argon2.verify(postPass, self.password)
