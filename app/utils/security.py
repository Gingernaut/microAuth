import jwt
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from schemas.user import User as UserSchema
from passlib.hash import argon2

from config import get_config

app_config = get_config()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(
    request: Request, token: str = Depends(oauth2_scheme)
) -> UserSchema:

    invalid_token_exception = HTTPException(
        status_code=401, detail=f"Invalid JWT token provided"
    )
    try:
        tokenData = jwt.decode(
            str(token), app_config.JWT_SECRET, algorithms=[app_config.JWT_ALGORITHM]
        )
        user = request.state.user_queries.get_user_by_id(tokenData["userId"])

        if not user:
            raise invalid_token_exception

        return UserSchema.from_orm(user)
    except:
        raise invalid_token_exception


async def get_admin_user(user: UserSchema = Depends(get_current_user)) -> UserSchema:
    if user.userRole != "ADMIN":
        raise HTTPException(status_code=403, detail=f"Admin credentials required")

    return user


def encrypt_password(plaintext_pass: str) -> str:
    return argon2.hash(plaintext_pass)
