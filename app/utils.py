import jwt
from passlib.hash import argon2

from config import get_config
from db_client import db
from models.users import User

appConfig = get_config()


def validate_admin_jwt(jwt_token):
    try:
        tokenData = jwt.decode(str(jwt_token), appConfig.JWT_SECRET, algorithms=[appConfig.JWT_ALGORITHM])
        account = get_account_by_id(tokenData['userId'])

        if account.userRole == "ADMIN":
            return tokenData
        else:
            return None

    except:
        return None


def validate_jwt_token(jwt_token):
    try:
        return jwt.decode(str(jwt_token), appConfig.JWT_SECRET, algorithms=[appConfig.JWT_ALGORITHM])
    except:
        return None


def encrypt_pass(password):
    return argon2.hash(password)


def get_account_by_email(emailAddress):
    return db.session.query(User).filter_by(emailAddress=emailAddress.lower()).first()


def get_account_by_id(id):
    return db.session.query(User).filter_by(id=id).first()


def format_body_params(body):
    newBody = {}
    if body.get('firstName'):
        newBody['firstName'] = body.get('firstName').title()

    if body.get('lastName'):
        newBody['lastName'] = body.get('lastName').title()

    if body.get('emailAddress'):
        newBody['emailAddress'] = body.get('emailAddress').lower()

    if body.get('phoneNumber'):
        newBody['phoneNumber'] = body.get('phoneNumber')

    if body.get('isValidated'):
        newBody['isValidated'] = bool(body.get('isValidated'))

    return newBody


def email_account_exists(emailAddr):
    if get_account_by_email(emailAddr):
        return True
    return False
