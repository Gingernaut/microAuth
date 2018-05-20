
import jwt
import pendulum
from sanic import Blueprint, response

from config import get_config
from models.resets import PasswordReset
from models.users import User
from db.db_client import db
from utils import emails, utils

appConfig = get_config()
email_bp = Blueprint("email_blueprint")


@email_bp.middleware("request")
async def sengrid_enabled(request):
    if not request.app.config["SENDGRID_API_KEY"]:
        return response.json({"error": "Sendgrid not configured"}, 500)


@email_bp.route("/confirm-account/<token>", methods=["POST"])
async def confirm_account(request, token):
    try:
        user = db.session.query(User).filter_by(UUID=token).first()

        if not user:
            return response.json({"error": "No user for given token"}, 400)

        user.isValidated = True
        db.session.commit()

        return response.json({"success": "User account confirmed"}, 200)

    except Exception as e:
        return utils.exeption_handler(e, "User confirmation failed", 500)


@email_bp.route("/reset-password/<emailAddress>", methods=["POST"])
async def send_reset_email(request, emailAddress):
    try:
        user = utils.get_account_by_email(emailAddress)
        if not user:
            return response.json({"error": "User not found"}, 404)

        reset = PasswordReset(user.userId)
        db.session.add(reset)
        db.session.commit()
        utils.send_reset_email(user, reset)

        return response.json({"message": "A reset email has been sent"}, 200)

    except Exception as e:
        return utils.exeption_handler(e, "Password reset failed", 500)


@email_bp.route("/confirm-reset/<token>", methods=["POST"])
async def reset(request, token):
    try:
        reset = db.session.query(PasswordReset).filter_by(id=token).first()
        if not token:
            return response.json({"error": "Invalid reset token"}, 404)

        if not token.isValid:
            return response.json({"error": "Reset token has already been used"}, 404)

        if pendulum.utcnow > reset.expireTime:
            return response.json({"error": "Reset token has expired."}, 400)

        # Invalidate all resets for this user
        db.session.query(PasswordReset).filter_by(userId=reset.userId).update(
            {"isValid": False}
        )
        db.session.commit()
        utils.send_reset_email(user, reset)

        return response.json({"message": "A reset email has been sent"}, 200)

    except Exception as e:
        return utils.exeption_handler(e, "Password reset confirmation failed", 500)
