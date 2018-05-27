from sanic import Sanic, response

from config import get_config
from db.db_client import db
from routes.admins import Admin_Endpoints, admin_bp
from routes.users import Account_Endpoints, user_bp
from routes.email import email_bp
from utils.logger import get_logger

import logging, sys, json_logging, sanic


def create_app(env=None):
    app = Sanic(__name__)
    app.config.from_object(get_config(env))

    # json_logging.ENABLE_JSON_LOGGING = app.config['JSON_LOGGING']
    # json_logging.ENABLE_JSON_LOGGING_DEBUG = False
    # json_logging.init(framework_name="sanic")
    # json_logging.init_request_instrument(app)

    # logger = get_logger("sanic-integration-test-app")

    db.init_engine(env)

    @app.listener("before_server_start")
    async def setup_connection(app, loop):
        db.connect()

    @app.listener("after_server_stop")
    async def close_connection(app, loop):
        db.close()

    if app.config["ENABLE_CORS"]:
        from sanic_cors import CORS

        CORS(app)

        @app.middleware("request")
        async def req_cors(request):
            if request.method == "OPTIONS":
                return response.HTTPResponse()

    # Routes
    @app.route("/")
    async def index(request):
        return response.json({"message": "/ reached"}, 200)

    app.blueprint(user_bp)
    app.blueprint(admin_bp)
    app.blueprint(email_bp)
    app.add_route(Account_Endpoints.as_view(), "/account")
    app.add_route(Admin_Endpoints.as_view(), "/accounts/<id>")

    return app
