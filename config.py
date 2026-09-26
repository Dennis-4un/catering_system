"""
Application configuration.

Reads everything from environment variables so secrets never live in code
(Section 27 of the spec: "Keep secrets and credentials in environment
variables"). Copy .env.example to .env and fill in real values for local
development.

DATABASE_URL defaults to a local SQLite file so the project runs out of the
box without a Postgres server installed. Point DATABASE_URL at a Postgres
instance for the "real" recommended stack — no code changes needed, since
Flask-SQLAlchemy/Flask-Migrate work against either.
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
    ALLOWED_UPLOAD_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # Flask-Mail (optional — safe no-op defaults for dev)
    #
    # To send real email through Gmail: enable 2-Step Verification on the
    # sending Gmail account, generate an "App Password" (Google Account ->
    # Security -> App Passwords — a regular Gmail password will NOT work
    # here), then set:
    #   MAIL_SERVER=smtp.gmail.com
    #   MAIL_PORT=587
    #   MAIL_USE_TLS=true
    #   MAIL_USERNAME=you@gmail.com
    #   MAIL_PASSWORD=<the 16-character app password>
    #   MAIL_DEFAULT_SENDER=you@gmail.com
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 25))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "no-reply@catering.local")

    # When False (default), customers can log in immediately after
    # registering even before clicking their confirmation email — this
    # matches the existing test suite's register-then-login flow and is
    # the safe default while MAIL_SERVER isn't yet pointed at a real SMTP
    # provider. Once real email delivery is confirmed working (see the
    # Gmail example above), set REQUIRE_EMAIL_VERIFICATION=true in your
    # .env to actually block unverified customers from logging in.
    REQUIRE_EMAIL_VERIFICATION = os.environ.get("REQUIRE_EMAIL_VERIFICATION", "false").lower() == "true"

    # Pagination default (Member 5's shared list utilities read this)
    ITEMS_PER_PAGE = 15


class DevelopmentConfig(BaseConfig):
     DEBUG = True
     SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{os.path.join(basedir, 'dev.db')}"
    
class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False  # simplifies posting test forms
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    def __init__(self):
        if not self.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError("DATABASE_URL must be set in production")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
