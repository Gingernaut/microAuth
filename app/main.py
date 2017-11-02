"""A basic (single function) API written using hug"""
from sanic import Sanic, response

from cli_helpers import init_db
from config import get_config
from db_client import db
from models.base import Base
from models.users import User
from routes.users import AccountRoutes, user_bp

app = Sanic()
app.config.from_object(get_config())


@app.listener("before_server_start")
async def setup_connection(app, loop):
    db.connect()


@app.listener("after_server_stop")
async def close_connection(app, loop):
    db.close()


@app.middleware('request')
async def cors(request):
    if request.method == 'OPTIONS':
        return response.HTTPResponse(status=200)


@app.middleware('response')
async def cors(request, response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'

# Routes
app.blueprint(user_bp)
app.add_route(AccountRoutes.as_view(), '/account')

if __name__ == '__main__':
    db.init_engine()
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=(app.config['IS_PROD'] == False))
