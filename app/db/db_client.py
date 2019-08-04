from sqlalchemy import create_engine, orm

from config import get_config
from models.base import Base


class SQLAlchemy:
    def __init__(self, autocommit=False):
        self.config = None
        self.engine = None
        self.sessionmaker = None
        self._conn_str = None
        self._autocommit = autocommit

    def new_session(self):
        return orm.scoped_session(self.sessionmaker)

    def get_conn_str(self):

        dbName = self.config.DB_NAME
        dbHost = self.config.DB_HOST
        dbPort = self.config.DB_PORT
        dbUser = self.config.DB_USERNAME
        dbPass = self.config.DB_PASSWORD

        return f"postgresql://{dbUser}:{dbPass}@{dbHost}:{dbPort}/{dbName}"

    def create_tables(self):
        session = self.new_session()
        Base.metadata.create_all(bind=self.engine)
        session.flush()
        session.remove()

    def initialize_connection(self, connection_env=None):
        self.config = get_config(connection_env)
        self._conn_str = self.get_conn_str()
        self.engine = create_engine(self._conn_str)

        self.sessionmaker = orm.sessionmaker(
            bind=self.engine,
            autoflush=True,
            autocommit=self._autocommit,
            expire_on_commit=True,
        )


db = SQLAlchemy()
