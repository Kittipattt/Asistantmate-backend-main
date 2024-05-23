# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize SQLAlchemy globally but not bind it to a specific Flask app
db = SQLAlchemy()


def create_app():
    """Create a Flask application using the app factory pattern."""
    app = Flask(__name__)

    # Configuration
    app.config.from_pyfile('config.py')  # Assuming you have a config.py for configurations

    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Apply CORS to all routes

    # Import and register blueprints
    from .api.attendance import attendance_api
    from .api.notification import notification_api
    from .api.cancellation import cancellation_api

    app.register_blueprint(attendance_api, url_prefix='/api/attendance')
    app.register_blueprint(notification_api, url_prefix='/api/notification')
    app.register_blueprint(cancellation_api, url_prefix='/api/cancellation')

    # Optionally, you can now also import and use your models if needed after initialization
    from .models.course import Course
    from .models.cancelled_class import CancelledClass

    return app
