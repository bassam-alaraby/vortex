import os

DEFAULT_MAX_CONTENT_LENGTH = 5 * 1024 * 1024


def _int_env(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def load_env_file(file_path=".env"):
    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key:
                continue

            if value and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]

            os.environ.setdefault(key, value)


load_env_file()

_secret_key = os.environ.get('SECRET_KEY')
if not _secret_key:
    raise RuntimeError("SECRET_KEY environment variable is not set")


class Config:
    SECRET_KEY = _secret_key
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = _int_env("MAX_CONTENT_LENGTH", DEFAULT_MAX_CONTENT_LENGTH)
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
    TURSO_DATABASE_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

class ProductionConfig(Config):
    DEBUG = False
    TEMPLATES_AUTO_RELOAD = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    return DevelopmentConfig
