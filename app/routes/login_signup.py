from fastapi import APIRouter, HTTPException
from starlette.responses import UJSONResponse
from starlette.requests import Request
from utils.security import encrypt_password
from utils import email
from schemas.user import UserCreate, LoggedInUser
from models.user import User as UserModel

router = APIRouter()


@router.post(
    "/signup",
    status_code=201,
    response_class=UJSONResponse,
    response_model=LoggedInUser,
)
async def signup(request: Request, userPayload: UserCreate):

    if request.state.user_queries.get_user_by_email(userPayload.emailAddress):
        raise HTTPException(
            status_code=409,
            detail=f"Account under {userPayload.emailAddress} already exists",
        )

    user = UserModel(
        firstName=userPayload.firstName,
        lastName=userPayload.lastName,
        emailAddress=userPayload.emailAddress.lower(),
        password=encrypt_password(userPayload.password),
        userRole="USER",
        isVerified=False,
    )

    new_account = request.state.user_queries.create_user(user)

    if request.state.config.SENDGRID_API_KEY:
        verify_reset = request.state.reset_queries.create_reset(user.id)

        if request.state.config.API_ENV != "TESTING":
            try:
                email.send_confirmation_email(user, verify_reset)
            except Exception as e:
                request.state.reset_queries.invalidate_resets_for_user(user.id)
                print(e.message)

    new_account.jwt = new_account.gen_token()
    return LoggedInUser.from_orm(new_account)


@router.post("/login", response_class=UJSONResponse, response_model=LoggedInUser)
async def login(request: Request, userPayload: UserCreate):
    existing_account = request.state.user_queries.get_user_by_email(
        userPayload.emailAddress
    )

    if not existing_account:
        raise HTTPException(
            status_code=404,
            detail=f"Account under {userPayload.emailAddress} does not exist",
        )

    if not existing_account.pass_matches(userPayload.password):
        raise HTTPException(status_code=403, detail="Incorrect password")

    existing_account.jwt = existing_account.gen_token()
    return LoggedInUser.from_orm(existing_account)
