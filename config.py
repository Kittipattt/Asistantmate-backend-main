import os


# Basic configuration
class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.urandom(24)  # Generates a random key; consider a fixed key for production
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///yourdatabase.db'  # Example: SQLite URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Development configuration
class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    # More development-specific settings can be added here
    # Example for a more complex DB system in development
    # SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/devdb'


# Testing configuration
class TestingConfig(Config):
    TESTING = True
    # Disable CSRF tokens in the testing configuration for easier form submissions
    WTF_CSRF_ENABLED = False


# Production configuration
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/proddb'
    # Other production-specific settings
    # Example: Data caching mechanisms, logging level, etc.


# Dictionary to hold all your configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Use the environment variable to determine which configuration to use
config_name = os.getenv('FLASK_CONFIG', 'default')
