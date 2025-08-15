import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    APPLICATION_ROOT = os.getenv("APPLICATION_ROOT", "/").rstrip("/")
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    STATIC_URL_PATH = os.getenv("STATIC_URL_PATH", "/forecast-web/static")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = "development"
    TESTING = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = "production"
    TESTING = False