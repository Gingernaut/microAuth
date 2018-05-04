import multiprocessing
import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path.cwd() / ".env"
load_dotenv(dotenv_path=env_path)


class BaseConfig:
    """Base configuration"""
    API_ENV = os.getenv("API_ENV", "DEVELOPMENT")
    DB_USERNAME = os.getenv("TEST_DB_USERNAME")
    DB_PASSWORD = os.getenv("TEST_DB_PASSWORD")
    DB_URL = "0.0.0.0:5432"
    DB_NAME = os.getenv("TEST_DB_USERNAME")
    ADMIN_EMAIL = os.getenv("TEST_ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD")
    TOKEN_TTL_HOURS = 158
    MIN_PASS_LENGTH = 6
    JWT_ALGORITHM = "HS256"
    HOST = "0.0.0.0"
    PORT = 5000
    WORKERS = 4


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    JWT_SECRET = "abcdefghijklmnopqrstuvwxyz12345678901234567890123456"


class TestingConfig(BaseConfig):
    """Testing configuration"""
    JWT_SECRET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    TOKEN_TTL_HOURS = 1


class ProductionConfig(BaseConfig):
    """Production configuration"""
    JWT_SECRET = os.getenv("JWT_SECRET")
    DB_URL = os.getenv("DB_URL")
    DB_NAME = os.getenv("DB_NAME")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    WORKERS = multiprocessing.cpu_count() * 2 + 1


def get_config(env=None):
    ENV_MAPPING = {
        "DEVELOPMENT": DevelopmentConfig,
        "PRODUCTION": ProductionConfig,
        "TESTING": TestingConfig
    }

    if not env:
        env = BaseConfig.API_ENV

    return ENV_MAPPING[env]
