from fastapi import APIRouter, Depends, HTTPException

from schemas.user import User, UserUpdate
from starlette.requests import Request
from starlette.responses import UJSONResponse
from utils.security import get_current_user, encrypt_password

router = APIRouter()


@router.get("/account", response_class=UJSONResponse, response_model=User)
async def get_account(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/account", response_class=UJSONResponse, response_model=User)
async def update_account(
    request: Request,
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    userModel = request.state.user_queries.get_user_by_id(current_user.id)

    if payload.userRole and current_user.userRole != "ADMIN":
        raise HTTPException(status_code=403, detail=f"Account cannot update own role")
    elif payload.userRole:
        userModel.userRole = payload.userRole

    if payload.emailAddress:
        existing_email_account = request.state.user_queries.get_user_by_email(
            payload.emailAddress
        )
        if existing_email_account and existing_email_account.id != current_user.id:
            raise HTTPException(
                status_code=403, detail=f"Account with that email already exists"
            )
        else:
            userModel.emailAddress = payload.emailAddress.lower()

    if payload.firstName:
        userModel.firstName = payload.firstName

    if payload.lastName:
        userModel.lastName = payload.lastName

    if payload.phoneNumber:
        userModel.phoneNumber = payload.phoneNumber

    if payload.password:
        userModel.password = encrypt_password(payload.password)

    request.state.user_queries.update_user(userModel)
    return User.from_orm(userModel)


@router.delete("/account", response_class=UJSONResponse)
async def delete_account(
    request: Request, current_user: User = Depends(get_current_user)
):
    request.state.user_queries.delete_user(current_user.id)
    return {"success": "Account deleted"}
