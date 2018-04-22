import os
from pathlib import Path

from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path, verbose=True)


class BaseConfig:
    """Base configuration"""
    DB_URL = os.getenv("DB_URL")
    DB_NAME = os.getenv("DB_NAME")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = str(os.getenv("ADMIN_PASSWORD"))
    IS_PROD = os.getenv("API_ENV") == "PRODUCTION"
    IS_TEST = os.getenv("API_ENV") == "TESTING"
    IS_DEV = os.getenv("API_ENV") == "DEVELOPMENT"
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = "HS256"
    TOKEN_TTL_HOURS = 158
    MIN_PASS_LENGTH = 6
    PORT = 5000


class DevelopmentConfig(BaseConfig):
    """Development configuration"""


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TOKEN_TTL_HOURS = 1
    DB_USERNAME = os.getenv("TEST_DB_USERNAME")
    DB_PASSWORD = os.getenv("TEST_DB_PASSWORD")
    DB_URL = "localhost"
    DB_NAME = os.getenv("TEST_DB_USERNAME")
    JWT_SECRET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class ProductionConfig(BaseConfig):
    """Production configuration"""


def get_config(env=None):
    ENV_MAPPING = {
        'DEVELOPMENT': DevelopmentConfig,
        'PRODUCTION': ProductionConfig,
        'TESTING': TestingConfig
    }

    if env:
        return ENV_MAPPING[env]
    else:
        return ENV_MAPPING[os.environ.get('API_ENV', 'DEVELOPMENT')]

    return config
