import jwt
import pendulum
from sanic import Blueprint, Sanic, response
from sanic.views import HTTPMethodView

from utils import utils
from config import get_config
from db.db_client import db
from models.users import User

user_bp = Blueprint("user_blueprint")


class Account_Endpoints(HTTPMethodView):

    decorators = [utils.authorized()]

    async def get(self, request):

        try:
            userId = utils.get_id_from_jwt(request)
            user = utils.get_account_by_id(userId)
            return response.json(user.serialize(), 200)
        except Exception as e:
            res = {"error": "User not found"}
            if request.app.config["API_ENV"] != "PRODUCTION":
                res["detailed"] = str(e)
            return response.json(res, 400)

    async def put(self, request):

        try:
            userId = utils.get_id_from_jwt(request)
            user = utils.get_account_by_id(userId)

            if not user:
                return response.json({"error": "User not found"}, 400)

            user.modifiedDate = pendulum.utcnow()
            cleanData = utils.format_body_params(request.json)

            if not cleanData:
                db.session.expire(user)
                return response.json({"error": "No valid data provided for update"}, 400)

            if cleanData.get("userRole") and user.userRole != "ADMIN":
                db.session.expire(user)
                return response.json({"error": "Cannot update role"}, 401)

            if cleanData.get("password"):
                providedPass = cleanData.get("password")
                if len(providedPass) < request.app.config["MIN_PASS_LENGTH"]:
                    db.session.expire(user)
                    return response.json({"error": "New password does not meet length requirements"}, 400)

                user.password = utils.encrypt_pass(providedPass)

            if cleanData.get("emailAddress"):
                newEmail = cleanData.get("emailAddress")

                if utils.email_account_exists(newEmail) and utils.get_account_by_email(newEmail).id != user.id:
                    db.session.expire(user)
                    return response.json({"error": "Email address associated with another account"}, 400)

                user.emailAddress = newEmail

            if cleanData.get("firstName"):
                user.firstName = cleanData.get("firstName")

            if cleanData.get("lastName"):
                user.lastName = cleanData.get("lastName")

            if cleanData.get("phoneNumber"):
                user.phoneNumber = cleanData.get("phoneNumber")

            if cleanData.get("isValidated"):
                user.isValidated = cleanData.get("isValidated")

            db.session.commit()
            res = user.serialize()
            res["success"] = "Account updated"
            return response.json(res, 200)

        except Exception as e:
            res = {"error": "Account update failed"}
            if request.app.config["API_ENV"] != "PRODUCTION":
                res["detailed"] = str(e)
            return response.json(res, 400)

    async def delete(self, request):
        try:
            userId = utils.get_id_from_jwt(request)
            db.session.query(User).filter_by(id=userId).delete()
            db.session.commit()
            return response.json({"success": "Account deleted"}, 200)

        except Exception as e:
            res = {"error": "Account deletion failed"}
            if request.app.config["API_ENV"] != "PRODUCTION":
                res["detailed"] = str(e)
            return response.json(res, 400)


@user_bp.route("/signup", methods=["POST"])
def signup(request):

    try:
        cleanData = utils.format_body_params(request.json)

        emailAddress = cleanData.get("emailAddress")
        password = request.json.get("password")
        firstName = cleanData.get("firstName")
        lastName = cleanData.get("lastName")
        phoneNumber = cleanData.get("phoneNumber")

        if not emailAddress:
            return response.json({"error": "No email address provided"}, 400)

        if not password:
            return response.json({"error": "No password provided"}, 400)

        if utils.email_account_exists(emailAddress):
            return response.json({"error": "An account with that email address already exists"}, 400)

        if len(password) < request.app.config["MIN_PASS_LENGTH"]:
            return response.json({"error": "Password does not meet required length requirements"}, 400)

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
        if request.app.config["API_ENV"] != "PRODUCTION":
            res["detailed"] = str(e)
        return response.json(res, 400)


@user_bp.route("/login", methods=["POST"])
def login(request):

    try:
        emailAddress = request.json.get("emailAddress")
        password = request.json.get("password")
        user = utils.get_account_by_email(emailAddress)

        if not user:
            return response.json({"error": "No account for provided email address"}, 400)

        if not user.pass_matches(password):
            return response.json({"error": "Invalid credentials"}, 400)

        return response.json(user.serialize(jwt=True), 200)

    except Exception as e:
        res = {"error": "login failed"}
        if request.app.config["API_ENV"] != "PRODUCTION":
            res["detailed"] = str(e)
        return response.json(res, 400)
