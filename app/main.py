
from db_client import db
from create_app import create_app


if __name__ == "__main__":
    app = create_app()
    db.init_engine()
    app.run(host="0.0.0.0",
            port=app.config["PORT"],
            workers=4,
            debug=(app.config["IS_PROD"] == False))
