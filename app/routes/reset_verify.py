from fastapi import APIRouter, HTTPException

from schemas.user import LoggedInUser
from starlette.responses import UJSONResponse
from starlette.requests import Request
from utils import email

import jwt
from config import get_config

router = APIRouter()
app_config = get_config()


@router.post(
    "/confirm-account/{token}",
    response_class=UJSONResponse,
    response_model=LoggedInUser,
)
def confirm_account(request: Request, token: str):
    try:
        user = get_user_from_token(request, token)
        user.isVerified = True
        request.state.user_queries.update_user(user)
        request.state.reset_queries.invalidate_resets_for_user(user.id)
        user.jwt = user.gen_token()

        return LoggedInUser.from_orm(user)
    except:
        raise HTTPException(403)


@router.post("/initiate-reset/{email_address}", response_class=UJSONResponse)
def send_reset_email(request: Request, email_address: str):
    user_account = request.state.user_queries.get_user_by_email(email_address)
    if not user_account:
        raise HTTPException(status_code=404)

    reset = request.state.reset_queries.create_reset(user_account.id)

    if request.state.config.API_ENV != "TESTING":
        email.send_reset_email(user_account, reset)

    return {"success": f"reset initiated for account {email_address}"}


@router.post(
    "/confirm-reset/{token}", response_class=UJSONResponse, response_model=LoggedInUser
)
def confirm_reset(request: Request, token: str):
    try:
        user = get_user_from_token(request, token)

        request.state.reset_queries.invalidate_resets_for_user(user.id)
        user.jwt = user.gen_token()
        return LoggedInUser.from_orm(user)
    except Exception as e:
        print(e)
        raise HTTPException(403)


def get_user_from_token(request: Request, token: str):

    try:
        tokenData = jwt.decode(
            token.replace("__DT__", "."),
            app_config.JWT_SECRET,
            algorithms=[app_config.JWT_ALGORITHM],
        )

        reset = request.state.reset_queries.get_reset_by_id(tokenData["id"])
        if not reset:
            print("no reset for token")
            raise HTTPException(status_code=404)
        elif not reset.isValid:
            print("invalid reset")
            raise HTTPException(status_code=403, detail="Reset token is expired")

        user = request.state.user_queries.get_user_by_id(tokenData["userId"])
        if not user:
            print("no user for token")
            raise HTTPException(status_code=404)
        return user
    except Exception as e:
        print(e)
        raise HTTPException(403)
