import multiprocessing
import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path.cwd() / ".env"
load_dotenv(dotenv_path=env_path, override=False)

# fmt: off


class BaseConfig:
    """Base configuration"""
    API_ENV = os.getenv("API_ENV", "DEVELOPMENT")
    LOGO = None  # Sanic logged logo
    DB_USERNAME = os.getenv("LOCAL_DB_USERNAME", NotImplementedError("db username required"))
    DB_PASSWORD = os.getenv("LOCAL_DB_PASSWORD", NotImplementedError("db password required"))
    DB_HOST = os.getenv("LOCAL_DB_HOST", NotImplementedError("db host required"))
    DB_PORT = os.getenv("LOCAL_DB_PORT", NotImplementedError("db port required"))
    DB_NAME = os.getenv("LOCAL_DB_USERNAME", NotImplementedError("db username required"))
    ADMIN_EMAIL = os.getenv("LOCAL_ADMIN_EMAIL", NotImplementedError("admin user email required"))
    ADMIN_PASSWORD = os.getenv("LOCAL_ADMIN_PASSWORD", NotImplementedError("admin user password required"))
    TOKEN_TTL_HOURS = 158
    PASSWORD_RESET_LINK_TTL_HOURS = 12
    MIN_PASS_LENGTH = 6
    JWT_ALGORITHM = "HS256"
    HOST = "0.0.0.0"
    PORT = 8000
    WORKERS = 4
    ENABLE_CORS = True

    # Sendgrid
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    FROM_ORG_NAME = os.getenv("FROM_ORG_NAME")
    FROM_WEBSITE_URL = os.getenv("FROM_WEBSITE_URL")


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    API_ENV = "DEVELOPMENT"
    JWT_SECRET = "abcdefghijklmnopqrstuvwxyz12345678901234567890123456"


class TestingConfig(BaseConfig):
    """Testing configuration"""
    API_ENV = "TESTING"
    JWT_SECRET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    TOKEN_TTL_HOURS = 1


class ProductionConfig(BaseConfig):
    """Production configuration"""
    API_ENV = "PRODUCTION"
    JWT_SECRET = os.getenv("JWT_SECRET", NotImplementedError("jwt secret required"))
    DB_HOST = os.getenv("DB_HOST", NotImplementedError("production db host required"))
    DB_PORT = os.getenv("DB_PORT", NotImplementedError("production db port required"))
    DB_NAME = os.getenv("DB_NAME", NotImplementedError("production db name required"))
    DB_USERNAME = os.getenv("DB_USERNAME", NotImplementedError("production db username required"))
    DB_PASSWORD = os.getenv("DB_PASSWORD", NotImplementedError("production db password required"))
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", NotImplementedError("production admin email required"))
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", NotImplementedError("production admin password required"))
    WORKERS = multiprocessing.cpu_count() * 2 + 1


def get_config(env=None):
    ENV_MAPPING = {
        "DEVELOPMENT": DevelopmentConfig,
        "PRODUCTION": ProductionConfig,
        "TESTING": TestingConfig,
    }

    if not env:
        env = BaseConfig.API_ENV

    return ENV_MAPPING[env]
# fmt: on
