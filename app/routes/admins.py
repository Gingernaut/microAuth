import jwt
import pendulum
from sanic import response
from sanic.views import HTTPMethodView

import utils
from config import get_config
from db_client import db
from models.users import User


class Admin_Endpoints(HTTPMethodView):
    decorators = [utils.authorized(admin=True)]

    async def get(self, id, token_data, response):
        user = utils.get_account_by_id(id)

        if user:
            return user.serialize()
        else:
            response.status = HTTP_400
            return "Account retrieval failed"

    async def put(self, id, token_data, response):

        try:
            user = db.session.query(User).filter_by(id=id).first()

            if not user:
                response.status = HTTP_400
                return "Account retrieval failed"

            if body.get('password'):
                if len(body.get('password')) < request.app.config['MIN_PASS_LENGTH']:
                    response.status = HTTP_400
                    return "New password does not meet length requirements"

                user.password = utils.encrypt_pass(body.get('password'))

            if body.get('userRole'):
                user.userRole = body.get('userRole').upper()

            cleanBody = utils.format_body_params(body)
            for k, v in cleanBody.items():
                user.k = v

            user.modifiedDate = pendulum.utcnow()
            db.session.commit()

            return "Successfully updated account"
        except Exception as e:
            print(e)
            response.status = HTTP_500
            return "update failed"

    async def delete(self, token_data, response):
        try:
            db.session.query(User).filter_by(id=token_data["userId"]).delete()
            db.session.commit()
            return "Successfully deleted account"
        except:
            response.status = HTTP_400
            return "Delete operation failed"


@user_bp.route("/accounts", methods=["OPTIONS", "GET"])
@utils.authorized(admin=True)
def get_users(request):
    users = db.session.query(User).all()
    return response.json({
        "users": [u.serialize() for u in users]
    }, 200)
