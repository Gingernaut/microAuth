import hug
import jwt
import pendulum
from falcon import HTTP_201, HTTP_400, HTTP_404, HTTP_500

import utils
from config import get_config
from db_client import db
from models.users import User

appConfig = get_config()
default_auth = hug.authentication.token(utils.validate_jwt_token)


@hug.object.urls('/account', requires=default_auth, parse_body=True)
class Account_Endpoints:

    @hug.object.get()
    def get_acc(self, token_data: hug.directives.user, response):

        user = utils.get_account_by_id(token_data['userId'])

        if user:
            return user.serialize()
        else:
            response.status = HTTP_400
            return "Account retrieval failed"

    @hug.object.put()
    def update_acc(self, token_data: hug.directives.user, body, response,
        firstName: hug.types.text=None):

        user = utils.get_account_by_id(token_data['userId'])
        if not user:
            response.status = HTTP_400
            return "Account retrieval failed"

        if body.get('password'):
            if len(body.get('password')) < appConfig.MIN_PASS_LENGTH:
                response.status = HTTP_400
                return "New password does not meet length requirements"

            user.password = utils.encrypt_pass(body.get('password'))

        cleanBody = utils.format_body_params(body)
        for k, v in cleanBody.items():
            user.k = v

        user.modifiedDate = pendulum.utcnow()
        db.session.commit()

        return "Successfully updated account"

    @hug.object.delete()
    def delete_acc(self, token_data: hug.directives.user, response):
        try:
            db.session.query(User).filter_by(id=token_data["userId"]).delete()
            db.session.commit()
            return "Successfully deleted account"
        except:
            response.status = HTTP_500
            return "account deletion failed"


@hug.post('/signup', status_code=HTTP_201)
def signup(emailAddress: hug.types.text,
           password: hug.types.text,
           response,
           body,
           firstName: hug.types.text=None,
           lastName: hug.types.text=None,
           phoneNumber: hug.types.text=None):

    try:
        print(body)
        print(type(body))
        if utils.email_account_exists(emailAddress):
            response.status = HTTP_400
            return "An account with that email address already exists"

        if len(password) < appConfig.MIN_PASS_LENGTH:
            response.status = HTTP_400
            return "Password does not meet length requirements"

        if firstName:
            firstName = firstName.title()
        if lastName:
            lastName = lastName.title()

        user = User(firstName=firstName,
                    lastName=lastName,
                    emailAddress=emailAddress.lower(),
                    password=utils.encrypt_pass(password),
                    phoneNumber=phoneNumber)

        db.session.add(user)
        db.session.commit()

        return user.serialize(jwt=True)

    except Exception as e:
        print(e)
        response.status = HTTP_400
        return "Signup failed"


@hug.post('/login')
def login(emailAddress: hug.types.text, password: hug.types.text, response):

    try:
        user = utils.get_account_by_email(emailAddress)

        if user.pass_matches(password):
            return user.serialize(jwt=True)
        else:
            response.status = HTTP_400
            return "Invalid credentials"

    except Exception as e:
        print(e)
        response.status = HTTP_400

        return "Login failed"
