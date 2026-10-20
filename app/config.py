import os
from datetime import timedelta
from decimal import Decimal

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "apnastore-dev-secret-key-4f29a0781c7e2b14")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Store settings
    STORE_NAME = "APNASTORE"
    STORE_TAGLINE = "Your Neighbourhood Store, Online."
    CURRENCY_SYMBOL = "₹"
    SHIPPING_FLAT_RATE = Decimal(os.environ.get("SHIPPING_FLAT_RATE", "60.00"))
    FREE_SHIPPING_THRESHOLD = Decimal(os.environ.get("FREE_SHIPPING_THRESHOLD", "999.00"))
    ITEMS_PER_PAGE = 12
    LOW_STOCK_THRESHOLD = 5

    # Session and Cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Upload settings
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4MB max upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "images", "uploads")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    instance_path = os.path.join(BASE_DIR, "instance")
    os.makedirs(instance_path, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{os.path.join(instance_path, 'apnastore.db')}"


class TestingConfig(Config):
    """Testing configuration with in-memory DB and disabled CSRF for test simplicity."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key-apnastore-suite"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    instance_path = os.path.join(BASE_DIR, "instance")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{os.path.join(instance_path, 'apnastore.db')}"


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
