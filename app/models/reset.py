import pendulum
import jwt
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey
from config import get_config
from models.base import Base

app_config = get_config()

# Model is also used when emailing a link to a user on signup


class PasswordReset(Base):
    __tablename__ = "password_reset"
    id = Column(BigInteger, primary_key=True)
    userId = Column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    createdTime = Column(DateTime, nullable=False, default=pendulum.now("UTC"))
    isValid = Column(Boolean, nullable=False, default=True)

    def __init__(self, userId):
        self.userId = userId

    def gen_token(self):
        payload = {
            "id": self.id,
            "userId": self.userId,
            "exp": pendulum.now("UTC").add(
                hours=int(app_config.PASSWORD_RESET_LINK_TTL_HOURS)
            ),
        }
        return str(
            jwt.encode(payload, app_config.JWT_SECRET, app_config.JWT_ALGORITHM).decode(
                "utf-8"
            )
        ).replace(".", "__DT__")
