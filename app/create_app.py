from sanic import Sanic, response

from config import get_config
from db.db_client import db
from routes.admins import Admin_Endpoints, admin_bp
from routes.users import Account_Endpoints, user_bp
from routes.email import email_bp


def create_app(env=None):
    app = Sanic(__name__)
    app.config.from_object(get_config(env))

    db.init_engine(env)

    @app.listener("before_server_start")
    async def setup_connection(app, loop):
        db.connect()

    @app.listener("after_server_stop")
    async def close_connection(app, loop):
        db.close()

    @app.middleware("request")
    async def req_cors(request):
        if request.app.config["ENABLE_CORS"] and request.method == "OPTIONS":
            return response.HTTPResponse(status=200)

    @app.middleware("response")
    async def res_cors(request, response):
        if request.app.config["ENABLE_CORS"]:
            # You should set this to the consumers host
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "*"

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
