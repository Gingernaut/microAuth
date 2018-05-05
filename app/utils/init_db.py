
import sys
sys.path.append("./app")

from config import get_config
from db.db_client import db
from models.base import Base
from models.users import User
from passlib.hash import argon2

def init_db(env=None):
    try:
        print(">Creating tables and default admin account. \n")

        appConfig = get_config(env)
        db.init_engine(env)
        Base.metadata.drop_all(bind=db.engine)
        db.create_tables()

        admin = User(emailAddress=appConfig.ADMIN_EMAIL,
                     password=argon2.hash(appConfig.ADMIN_PASSWORD), userRole="ADMIN", isValidated=True)

        db.session.add(admin)
        db.session.commit()
        db.close()

        print("---------")
        print("Database succesfully initialized")
        print("---------")

    except Exception as e:
        print("---------")
        print(e)
        print("---------")


if __name__ == "__main__":
    init_db()
