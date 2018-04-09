import hug
import jwt
import pendulum
from falcon import HTTP_201, HTTP_400, HTTP_404, HTTP_500

import utils
from config import get_config
from db_client import db
from models.users import User

appConfig = get_config()
admin_auth = hug.authentication.token(utils.validate_admin_jwt)


@hug.object.urls('/account/{id}', requires=admin_auth)
class Admin_Endpoints:

    @hug.object.get()
    def get_acc(self, id: hug.types.number, token_data: hug.directives.user, response):
        user = utils.get_account_by_id(id)

        if user:
            return user.serialize()
        else:
            response.status = HTTP_400
            return "Account retrieval failed"

    @hug.object.put()
    def update_acc(self, id: hug.types.number, token_data: hug.directives.user, response):

        try:
            user = db.session.query(User).filter_by(id=id).first()

            if not user:
                response.status = HTTP_400
                return "Account retrieval failed"

            if body.get('password'):
                if len(body.get('password')) < appConfig.MIN_PASS_LENGTH:
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

    @hug.object.delete()
    def delete_acc(self, token_data: hug.directives.user, response):
        try:
            db.session.query(User).filter_by(id=token_data["userId"]).delete()
            db.session.commit()
            return "Successfully deleted account"
        except:
            response.status = HTTP_400
            return "Delete operation failed"


@hug.get('/accounts', requires=admin_auth)
def get_users():
    users = db.session.query(User).all()
    return {
        "users": [u.serialize() for u in users]
    }
