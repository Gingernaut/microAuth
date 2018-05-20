from functools import wraps

import jwt
from passlib.hash import argon2
from sanic import response

from config import get_config
from db.db_client import db
from models.users import User

appConfig = get_config()


def authorized(requireAdmin=False):

    def decorator(f):

        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            userId = get_id_from_jwt(request)

            if not userId:
                return response.json({"error": "Not Authorized"}, 401)

            if requireAdmin == True:
                user = get_account_by_id(userId)
                if not user or user.userRole != "ADMIN":
                    return response.json({"error": "Not Authorized"}, 401)

            return await f(request, *args, **kwargs)

        return decorated_function

    return decorator


def get_id_from_jwt(request):
    try:
        jwtToken = request.headers.get("authorization")
        tokenData = jwt.decode(
            str(jwtToken), appConfig.JWT_SECRET, algorithms=[appConfig.JWT_ALGORITHM]
        )
        return tokenData["userId"]
    except:
        return None


def encrypt_pass(password):
    return argon2.hash(password)


def get_account_by_email(emailAddress):
    return db.session.query(User).filter_by(emailAddress=emailAddress.lower()).first()


def email_account_exists(emailAddr):
    if get_account_by_email(emailAddr):
        return True
    return False


def get_account_by_id(id):
    return db.session.query(User).filter_by(id=id).first()


def format_body_params(body):
    newBody = {}
    if body.get("firstName"):
        newBody["firstName"] = body.get("firstName").title()

    if body.get("lastName"):
        newBody["lastName"] = body.get("lastName").title()

    if body.get("emailAddress"):
        newBody["emailAddress"] = body.get("emailAddress").lower()

    if body.get("password"):
        newBody["password"] = body.get("password")

    if body.get("phoneNumber"):
        newBody["phoneNumber"] = body.get("phoneNumber")

    if body.get("isValidated"):
        newBody["isValidated"] = bool(body.get("isValidated"))

    if body.get("userRole"):
        newBody["userRole"] = body.get("userRole").upper()

    return newBody


def exeption_handler(err, message, statuscode):

    res = {"error": message}
    if appConfig.API_ENV != "PRODUCTION":
        res["detailed"] = str(err)

    return response.json(res, statuscode)
