import jwt
import pendulum
from sanic import response
from sanic.views import HTTPMethodView

import utils
from config import get_config
from db_client import db
from models.users import User
from sanic import Blueprint, response

admin_bp = Blueprint("admin_blueprint")


class Admin_Endpoints(HTTPMethodView):
    decorators = [utils.authorized(admin=True)]

    async def get(self, request, id):
        try:
            return utils.get_account_by_id(id).serialize()

        except Exception as e:
            res = {"error": "Account lookup failed"}
            if not request.app.config['IS_PROD']:
                res['detailed'] = str(e)
            return response.json(res, 400)

    async def put(self, request, id):

        try:
            user = utils.get_account_by_id(id)

            if not user:
                return response.json({"error": "Account lookup failed"}, 400)

            user.modifiedDate = pendulum.utcnow()
            cleanData = utils.format_body_params(request.json)
            providedPassword = request.json.get("password")

            if providedPassword:
                if len(providedPassword) < request.app.config['MIN_PASS_LENGTH']:
                    return response.json({"error": "New password does not meet length requirements"}, 400)

                user.password = utils.encrypt_pass(providedPassword)

            if request.json.get("userRole"):
                user.userRole = request.json.get("userRole").uppper()

            if cleanData.get("emailAddress"):
                newEmail = cleanData.get("emailAddress")

                if utils.email_account_exists(newEmail) and utils.get_account_by_email(newEmail).id != user.id:
                    return response.json({"error": "Email address associated with another account"}, 400)

                user.emailAddress = newEmail

            if cleanData.get("firstName"):
                user.firstName = cleanData.get("firstName")

            if cleanData.get("lastName"):
                user.firstName = cleanData.get("lastName")

            if cleanData.get("phoneNumber"):
                user.firstName = cleanData.get("phoneNumber")

            if cleanData.get("isValidated"):
                user.firstName = cleanData.get("isValidated")

            db.session.commit()
            return response.json({"success": "Account updated"}, 200)

        except Exception as e:
            res = {"error": "Account update failed"}
            if not request.app.config['IS_PROD']:
                res['detailed'] = str(e)
            return response.json(res, 400)

    async def delete(self, request, id):
        try:
            db.session.query(User).filter_by(id=id).delete()
            db.session.commit()
            return "Successfully deleted account"

        except Exception as e:
            res = {"error": "Account deletion failed"}
            if not request.app.config['IS_PROD']:
                res['detailed'] = str(e)
            return response.json(res, 400)


@admin_bp.route("/accounts", methods=["GET"])
@utils.authorized(admin=True)
def get_users(request):
    users = db.session.query(User).all()
    return response.json({
        "users": [u.serialize() for u in users]
    }, 200)
