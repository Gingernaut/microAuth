import jwt
import pendulum
from sanic import Blueprint, Sanic, response
from sanic.views import HTTPMethodView

import utils
from config import get_config
from db_client import db
from models.users import User

user_bp = Blueprint("user_blueprint")


class AccountRoutes(HTTPMethodView):

    decorators = [utils.authorized()]

    async def get(self, request):

        try:
            userId = utils.get_id_from_jwt(request)
            user = utils.get_account_by_id(userId)
            return response.json(user.serialize(), 200)
        except Exception as e:
            res = {"error": "Account lookup failed"}
            if not request.app.config['IS_PROD']:
                res['detailed'] = str(e)
            return response.json(res, 400)

    async def put(self, request):

        try:
            userId = utils.get_id_from_jwt(request)
            user = utils.get_account_by_id(userId)
            user.modifiedDate = pendulum.utcnow()
            body = request.body

            if body.get("password"):
                if len(body.get("password")) < request.app.config['MIN_PASS_LENGTH']:
                    return response.json({"error": "New password does not meet length requirements"}, 400)

                user.password = utils.encrypt_pass(body.get("password"))

            if body.get("emailAddress"):
                newEmail = body.get("emailAddress")

                if utils.email_account_exists(newEmail) and utils.get_account_by_email(newEmail).id != user.id:
                    return response.json({"error": "Email address associated with another account"}, 400)

            cleanData = utils.format_body_params(body)
            for k, v in cleanBody.items():
                user.k = v

            db.session.commit()
            return response.json({"success": "Account updated"}, 200)

        except Exception as e:
            res = {"error": "Account update failed"}
            if not request.app.config['IS_PROD']:
                res['detailed'] = str(e)
            return response.json(res, 400)

    async def delete(self, request):
        try:
            userId = utils.get_id_from_jwt(request)
            db.session.query(User).filter_by(id=userId).delete()
            db.session.commit()
            return response.json({"success": "Account deleted"}, 200)

        except Exception as e:
            res = {"error": "Account deletion failed"}
            if not request.app.config['IS_PROD']:
                res['detailed'] = str(e)
            return response.json(res, 400)


@user_bp.route("/signup", methods=["OPTIONS", "POST"])
def signup(request):

    try:
        cleanData = utils.format_body_params(request.body)

        emailAddress = cleanData.get('emailAddress')
        password = request.body.get('password')
        firstName = cleanData.get('firstName')
        lastName = cleanData.get('lastName')
        phoneNumber = cleanData.get('phoneNumber')

        if utils.email_account_exists(emailAddress):
            return response.json({"error": "An account with that email address already exists"}, 400)

        if len(password) < request.app.config['MIN_PASS_LENGTH']:
            return response.json({"error": "password does not meet required length requirements"}, 400)

        user = User(firstName=firstName,
                    lastName=lastName,
                    emailAddress=emailAddress,
                    password=utils.encrypt_pass(password),
                    phoneNumber=phoneNumber)

        db.session.add(user)
        db.session.commit()

        return response.json(user.serialize(jwt=True), 201)

    except Exception as e:
        res = {"error": "Signup failed"}
        if not request.app.config['IS_PROD']:
            res['detailed'] = str(e)
        return response.json(res, 400)


@user_bp.route("/login", methods=["OPTIONS", "POST"])
def login(request):

    try:
        cleanData = utils.format_body_params(request.body)
        emailAddress = cleanData.get('emailAddress')
        password = request.body.get('password')
        user = utils.get_account_by_email(emailAddress)

        if not user:
            return response.json({"error": "No account for provided email address"}, 400)

        if not user.pass_matches(password):
            return response.json({"error": "Invalid credentials"}, 400)

        return response.json(user.serialize(jwt=True), 200)

    except Exception as e:
        res = {"error": "login failed"}
        if not request.app.config['IS_PROD']:
            res['detailed'] = str(e)
        return response.json(res, 400)
