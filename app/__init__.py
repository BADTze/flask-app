import os
import logging
from flask import Flask
from flask_caching import Cache
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig

# Load .env variables
load_dotenv()

# Global cache and logger
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
logger = logging.getLogger(__name__)

def create_app(config_class=None):
    try:
        if config_class is None:
            env = os.getenv("FLASK_ENV", "development").lower()
            config_class = ProductionConfig if env == "production" else DevelopmentConfig
        
        app = Flask(__name__, static_url_path=config_class.STATIC_URL_PATH)

        app.config.from_object(config_class)
        app.config["CACHE_TYPE"] = os.getenv("CACHE_TYPE", "SimpleCache")
        app.config["CACHE_DEFAULT_TIMEOUT"] = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 3600)) 

        # configure_logging(app)
        cache.init_app(app)
        register_blueprints(app)

        # Tampilkan semua rute saat startup
        print("\n📌 URL Map:")
        for rule in app.url_map.iter_rules():
            print(f"📌 Route: {rule} → {rule.endpoint}")
        print()

        return app 

    except Exception as e:
        logger.exception("❌ Failed to initialize application")
        raise

# def configure_logging(app):
#     log_level = logging.INFO
#     log_format = "%(asctime)s [%(levelname)s] %(message)s"

#     logging.basicConfig(
#         level=log_level,
#         format=log_format,
#         handlers=[
#             logging.FileHandler("logs/app.log", mode="a", encoding="utf-8"),
#             logging.StreamHandler()
#         ]
#     )

#     app.logger.setLevel(log_level)
#     for handler in logging.getLogger().handlers:
#         app.logger.addHandler(handler)

def register_blueprints(app):
    # from app.routes.pages import pages_bp
    from app.routes.api import api_bp

    # app.register_blueprint(pages_bp, url_prefix='/forecast-web')
    app.register_blueprint(api_bp, url_prefix='/forecast-web/api')
