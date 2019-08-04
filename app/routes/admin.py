from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from schemas.user import User as UserRead, UserUpdate
from starlette.requests import Request

from typing import List
from starlette.responses import UJSONResponse

from utils.security import get_admin_user, encrypt_password

router = APIRouter()


@router.get(
    "/accounts/{user_id}", response_model=UserRead, response_class=UJSONResponse
)
async def get_user(
    request: Request, user_id: int, current_user: User = Depends(get_admin_user)
):
    user = request.state.user_queries.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"Account not found")
    return user


@router.put(
    "/accounts/{user_id}", response_model=UserRead, response_class=UJSONResponse
)
async def update_user(
    request: Request,
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(get_admin_user),
):

    userModel = request.state.user_queries.get_user_by_id(user_id)

    if not userModel:
        raise HTTPException(status_code=404, detail=f"Account not found")

    if payload.userRole:
        userModel.userRole = payload.userRole

    if payload.firstName:
        userModel.firstName = payload.firstName

    if payload.lastName:
        userModel.lastName = payload.lastName

    if payload.phoneNumber:
        userModel.phoneNumber = payload.phoneNumber

    if payload.password:
        userModel.password = encrypt_password(payload.password)

    request.state.user_queries.update_user(userModel)
    return UserRead.from_orm(userModel)


@router.delete("/accounts/{user_id}", response_class=UJSONResponse)
async def delete_user(
    request: Request, user_id: int, current_user: User = Depends(get_admin_user)
):
    request.state.user_queries.delete_user(user_id)
    return {}


@router.get("/accounts", response_model=List[UserRead], response_class=UJSONResponse)
async def get_all_users(request: Request, current_user: User = Depends(get_admin_user)):
    return request.state.user_queries.get_all_users()
