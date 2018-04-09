"""A basic (single function) API written using hug"""
import hug

from cli_helpers import init_db
from config import get_config
from db_client import db
from models.base import Base
from models.users import User
from routes import admins as adminRoutes
from routes import email as emailRoutes
from routes import users as userRoutes

appConfig = get_config()

# will disable documentation
# @hug.not_found()
# def not_found_handler():
#     return "Not Found"

# Adding all endpoints defined in ./routes


@hug.extend_api()
def with_other_apis():
    return [userRoutes, emailRoutes, adminRoutes]


app = hug.API(__name__)
db.init_app(app)

if __name__ == "__main__" and appConfig.API_ENV != "PRODUCTION":
    init_db.interface.cli()
