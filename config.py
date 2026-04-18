import os

class Config:
    # Use environment variables if available, otherwise use defaults
    SECRET_KEY = os.environ.get('SECRET_KEY', 'vortexMO')
    
    # Path to database, defaulting to local SQLite DB
    # The cs50 SQL library handles the 'sqlite:///' prefix automatically in most cases
    # but we'll store the full string here
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'sqlite:///database/app.db')
    
    TEMPLATES_AUTO_RELOAD = True
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # Ensure secure cookies in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
