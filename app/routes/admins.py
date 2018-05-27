import pendulum
from sanic import Blueprint, response
from sanic.views import HTTPMethodView

from db.db_client import db
from models.users import User
from utils import utils

admin_bp = Blueprint("admin_blueprint")


@admin_bp.route("/accounts", methods=["GET"])
@utils.authorized(requireAdmin=True)
async def get_users(request):
    users = db.session.query(User).all()
    return response.json({"users": [u.serialize() for u in users]}, 200)


class Admin_Endpoints(HTTPMethodView):
    decorators = [utils.authorized(requireAdmin=True)]

    async def get(self, request, id):
        try:
            user = utils.get_account_by_id(id)
            if not user:
                return response.json({"error": "User not found"}, 404)

            return response.json(user.serialize(), 200)

        except Exception as e:
            return utils.exeption_handler(e, "User not found", 400)

    async def put(self, request, id):
        # try:
        user = utils.get_account_by_id(id)

        if not user:
            return response.json({"error": "User not found"}, 404)

        user.modifiedTime = pendulum.now("UTC")
        cleanData = utils.format_body_params(request.json)

        if not cleanData:
            # db.session.rollback()
            return response.json({"error": "No valid data provided for update"}, 400)

        if cleanData.get("password"):
            providedPass = cleanData.get("password")
            if len(providedPass) < request.app.config["MIN_PASS_LENGTH"]:
                # db.session.rollback()
                return response.json(
                    {"error": "New password does not meet length requirements"}, 400
                )

            user.password = utils.encrypt_pass(providedPass)

        if request.json.get("userRole"):
            user.userRole = cleanData.get("userRole").upper()

        if cleanData.get("emailAddress"):
            newEmail = cleanData.get("emailAddress")

            if (
                utils.email_account_exists(newEmail)
                and utils.get_account_by_email(newEmail).id != user.id
            ):
                # db.session.rollback()
                return response.json(
                    {"error": "Email address associated with another account"}, 400
                )

            user.emailAddress = newEmail

        if cleanData.get("firstName"):
            user.firstName = cleanData.get("firstName")

        if cleanData.get("lastName"):
            user.lastName = cleanData.get("lastName")

        if cleanData.get("phoneNumber"):
            user.phoneNumber = cleanData.get("phoneNumber")

        if cleanData.get("isVerified"):
            user.isVerified = cleanData.get("isVerified")

        db.session.commit()
        res = user.serialize()
        res["success"] = "Account updated"
        return response.json(res, 200)

        # except Exception as e:
        #     return utils.exeption_handler(e, "Account update failed", 400)

    async def delete(self, request, id):
        try:
            db.session.query(User).filter_by(id=id).delete()
            db.session.commit()
            return response.json({"success": "Account deleted"}, 200)

        except Exception as e:
            return utils.exeption_handler(e, "Account deletion failed", 400)
