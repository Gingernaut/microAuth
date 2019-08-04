import time
import pendulum
from fastapi import FastAPI
from starlette.requests import Request
from config import get_config

from routes import admin, account, login_signup, reset_verify
from db.db_client import db
from db.user_queries import UserQueries
from db.reset_queries import PasswordResetQueries
from utils.logger import create_logger

log = create_logger(__name__)


def setup_middleware(app, configuration):

    if configuration.ENABLE_CORS:
        from starlette.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.middleware("http")
    async def add_config(request: Request, call_next):
        request.state.config = configuration
        return await call_next(request)

    @app.middleware("http")
    async def db_connection_manager(request: Request, call_next):
        db_session = db.new_session()
        try:
            request.state.user_queries = UserQueries(db_session)
            request.state.reset_queries = PasswordResetQueries(db_session)

            response = await call_next(request)

            db_session.flush()
            return response
        finally:
            db_session.remove()

    @app.middleware("http")
    async def add_headers_and_log(request: Request, call_next):

        start_time = time.time()
        response = await call_next(request)
        process_time_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-process-time-ms"] = str(process_time_ms)

        request_data = {
            "method": request.method,
            "path": request.url.path,
            "request_time": pendulum.from_timestamp(start_time).to_datetime_string(),
            "client": {"host": request.client.host, "port": request.client.port},
            "elapsed_ms": str(process_time_ms),
            "status_code": response.status_code,
        }

        log.info(request_data)
        return response


def setup_db_connection(app, configuration):
    @app.on_event("startup")
    async def startup_event():
        db.initialize_connection(configuration.API_ENV)

    @app.on_event("shutdown")
    def shutdown_event():
        db.sessionmaker.close_all()


def create_app(configuration):

    app = FastAPI()

    app.include_router(admin.router)
    app.include_router(account.router)
    app.include_router(login_signup.router)

    # only enable account confirmation and resets if emails can be sent
    if configuration.SENDGRID_API_KEY:
        app.include_router(reset_verify.router)

    setup_middleware(app, configuration)
    setup_db_connection(app, configuration)

    log.info("-----------")
    log.info(f"Created {configuration.API_ENV} application")
    log.info("-----------")
    return app


# called from uvicorn in `main.py`
if __name__ == "create_app":
    configuration = get_config()
    app = create_app(configuration)
