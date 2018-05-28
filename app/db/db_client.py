from sqlalchemy import create_engine, orm

from config import get_config
from models.base import Base

# https://github.com/fantix/gino ?


class SQLAlchemy:
    def __init__(self, autocommit=False):
        self.engine = None
        self.session = None
        self._conn_str = None
        self._autocommit = autocommit

    def connect(self):
        sm = orm.sessionmaker(
            bind=self.engine,
            autoflush=True,
            autocommit=self._autocommit,
            expire_on_commit=True,
        )

        self.session = orm.scoped_session(sm)

    def close(self):
        self.session.flush()
        self.session.close()
        self.session.remove()

    def get_conn_str(self):

        dbName = self.config.DB_NAME
        dbUrl = self.config.DB_URL
        dbUser = self.config.DB_USERNAME
        dbPass = self.config.DB_PASSWORD

        return f"postgresql://{dbUser}:{dbPass}@{dbUrl}/{dbName}"

    def create_tables(self):
        self.connect()
        Base.metadata.create_all(bind=self.engine)
        self.close()

    def init_engine(self, connection_env=None):
        self.config = get_config(connection_env)
        self._conn_str = self.get_conn_str()
        self.engine = create_engine(self._conn_str)


db = SQLAlchemy()
