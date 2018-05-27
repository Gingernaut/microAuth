
import sys
import time

sys.path.append("./app")

from passlib.hash import argon2

from config import get_config
from db.db_client import db
from models.base import Base
from models.users import User
from models.resets import PasswordReset


def init_db(env=None):
    print("\n")

    try:
        appConfig = get_config(env)

        if appConfig.API_ENV == "PRODUCTION":
            for i in range(5, -1, -1):
                print(
                    f">Running initalization against PRODUCTION database in {i} seconds...",
                    end="\r",
                )
                time.sleep(1)
            print("\n")

        print(">Creating tables and default admin account. \n")
        db.init_engine(env)
        Base.metadata.drop_all(bind=db.engine)
        db.create_tables()

        admin = User(
            emailAddress=appConfig.ADMIN_EMAIL,
            password=argon2.hash(appConfig.ADMIN_PASSWORD),
            userRole="ADMIN",
            isVerified=True,
        )

        db.session.add(admin)
        db.session.commit()
        db.close()

        print("---------")
        print(">Database succesfully initialized")
        print("---------")

    except Exception as e:
        print("---------")
        print(e)
        print("---------")


if __name__ == "__main__":
    init_db()
