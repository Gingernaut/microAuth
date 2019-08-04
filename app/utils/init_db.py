# flake8: noqa
import sys
import time

sys.path.append("./app")

from config import get_config
from db.db_client import db
from models.base import Base
from models.user import User
from models.reset import PasswordReset
from passlib.hash import argon2

# All models must be imported so the appropriate tables are created


def init_db(env=None):
    try:
        app_config = get_config(env)

        if app_config.API_ENV == "PRODUCTION":
            should_run = input(
                "!! Running database initialization against PRODUCTION database. This will delete all data & tables. \n Do you want to proceed? [Y/N]  "
            )
            if should_run.upper() != "Y":
                print("exiting DB intialization script")
                exit(0)

        print("---------")
        print(">Creating tables and default admin account. \n")
        db.initialize_connection(app_config.API_ENV)
        db.sessionmaker.close_all()

        print("dropping tables")
        Base.metadata.drop_all(bind=db.engine)
        print("creating new tables")
        db.create_tables()
        print("adding admin")
        admin = User(
            emailAddress=app_config.ADMIN_EMAIL,
            password=argon2.hash(app_config.ADMIN_PASSWORD),
            userRole="ADMIN",
            isVerified=True,
        )
        session = db.new_session()

        session.add(admin)
        session.commit()
        session.remove()

        print("---------")
        print(">Database succesfully initialized")
        print("---------")

    except Exception as e:
        print("---------")
        print(e)
        print("---------")


if __name__ == "__main__":
    init_db()
